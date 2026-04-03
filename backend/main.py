"""OviGuide Cutoff API — FastAPI + asyncpg."""

from __future__ import annotations

import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Header, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from database import get_pool, close_pool, get_connection
from models import (
    CutoffRow,
    IngestRequest,
    IngestResponse,
    CutoffOut,
    PaginatedCutoffs,
    TrendPoint,
    RoundProgressionPoint,
    UserIn,
    UserOut,
)

load_dotenv()
API_KEY: str = os.getenv("API_KEY", "")
ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "oviguide2026")
FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173")


@asynccontextmanager
async def lifespan(application: FastAPI):
    await get_pool()
    yield
    await close_pool()


app = FastAPI(
    title="OviGuide Cutoff API",
    version="1.0.0",
    description="Backend for storing and querying JoSAA counselling cutoff data.",
    lifespan=lifespan,
)

# CORS — allow the frontend origin (and localhost for dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "http://localhost:5173", "http://localhost:4173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def _verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")


# ── POST /ingest ──────────────────────────────────────────────────────────────

@app.post("/ingest", response_model=IngestResponse, tags=["ingest"])
async def ingest_cutoffs(body: IngestRequest, x_api_key: str = Header(...)):
    """Bulk-insert cutoff rows. Uses INSERT ... ON CONFLICT DO NOTHING for idempotency.

    Expects `X-API-Key` header. Each row should match the snake_cased JoSAA CSV
    columns — see the `CutoffRow` schema for the exact shape.
    """
    _verify_api_key(x_api_key)

    sql = """
        INSERT INTO cutoffs (year, round, institute, program, quota, seat_type, opening_rank, closing_rank)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        ON CONFLICT ON CONSTRAINT uq_cutoff_row DO NOTHING
    """
    inserted = 0
    async with get_connection() as conn:
        # Use a transaction for the whole batch
        async with conn.transaction():
            for row in body.rows:
                program = row.academic_program_name
                result = await conn.execute(
                    sql,
                    row.year, row.round, row.institute, program,
                    row.quota, row.seat_type, row.opening_rank, row.closing_rank,
                )
                # asyncpg returns e.g. "INSERT 0 1" or "INSERT 0 0"
                if result and result.endswith("1"):
                    inserted += 1

    total = len(body.rows)
    return IngestResponse(inserted=inserted, skipped=total - inserted, total=total)


# ── GET /cutoffs ──────────────────────────────────────────────────────────────

@app.get("/cutoffs", response_model=PaginatedCutoffs, tags=["query"])
async def list_cutoffs(
    institute: Optional[str] = Query(None),
    program: Optional[str] = Query(None),
    quota: Optional[str] = Query(None),
    seat_type: Optional[str] = Query(None),
    year: Optional[int] = Query(None),
    round: Optional[int] = Query(None),
    closing_rank_lte: Optional[int] = Query(None, description="Closing rank ≤ this value"),
    closing_rank_gte: Optional[int] = Query(None, description="Closing rank ≥ this value"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
):
    """Query cutoffs with optional filters and pagination."""
    conditions: list[str] = []
    params: list = []
    idx = 1

    for col, val in [
        ("institute", institute), ("program", program), ("quota", quota),
        ("seat_type", seat_type), ("year", year), ("round", round),
    ]:
        if val is not None:
            conditions.append(f"{col} = ${idx}")
            params.append(val)
            idx += 1
    if closing_rank_lte is not None:
        conditions.append(f"closing_rank <= ${idx}")
        params.append(closing_rank_lte)
        idx += 1
    if closing_rank_gte is not None:
        conditions.append(f"closing_rank >= ${idx}")
        params.append(closing_rank_gte)
        idx += 1

    where = "WHERE " + " AND ".join(conditions) if conditions else ""
    offset = (page - 1) * page_size

    async with get_connection() as conn:
        total = await conn.fetchval(f"SELECT count(*) FROM cutoffs {where}", *params)
        rows = await conn.fetch(
            f"SELECT * FROM cutoffs {where} ORDER BY year DESC, round DESC, closing_rank ASC LIMIT ${idx} OFFSET ${idx+1}",
            *params, page_size, offset,
        )

    return PaginatedCutoffs(
        data=[CutoffOut(**dict(r)) for r in rows],
        total=total, page=page, page_size=page_size,
    )



# ── GET /institutes ───────────────────────────────────────────────────────────

@app.get("/institutes", response_model=list[str], tags=["query"])
async def list_institutes():
    """Return distinct list of all institutes in the DB."""
    async with get_connection() as conn:
        rows = await conn.fetch("SELECT DISTINCT institute FROM cutoffs ORDER BY institute")
    return [r["institute"] for r in rows]


# ── GET /programs ─────────────────────────────────────────────────────────────

@app.get("/programs", response_model=list[str], tags=["query"])
async def list_programs(institute: Optional[str] = Query(None)):
    """Return distinct programs, optionally filtered by institute."""
    if institute:
        rows_q = "SELECT DISTINCT program FROM cutoffs WHERE institute = $1 ORDER BY program"
        async with get_connection() as conn:
            rows = await conn.fetch(rows_q, institute)
    else:
        async with get_connection() as conn:
            rows = await conn.fetch("SELECT DISTINCT program FROM cutoffs ORDER BY program")
    return [r["program"] for r in rows]


# ── GET /rank-check ───────────────────────────────────────────────────────────

@app.get("/rank-check", response_model=list[CutoffOut], tags=["prediction"])
async def rank_check(
    rank: int = Query(..., ge=1, description="Student's CRL rank"),
    year: int = Query(..., ge=2015),
    quota: str = Query(..., pattern=r"^(HS|OS|AI)$"),
    seat_type: str = Query("Gender-Neutral"),
    round: Optional[int] = Query(None, description="Specific round; defaults to latest available"),
    limit: int = Query(200, ge=1, le=1000),
):
    """Core prediction endpoint. Returns all rows where closing_rank >= rank
    (i.e. seats the student could have secured), ordered by closing rank
    ascending so tighter / more competitive cutoffs appear first.
    """
    conditions = ["closing_rank >= $1", "year = $2", "quota = $3", "seat_type = $4"]
    params: list = [rank, year, quota, seat_type]
    idx = 5
    if round is not None:
        conditions.append(f"round = ${idx}")
        params.append(round)
        idx += 1

    where = " AND ".join(conditions)
    params.append(limit)

    sql = f"""
        SELECT * FROM cutoffs
        WHERE {where}
        ORDER BY closing_rank ASC
        LIMIT ${idx}
    """
    async with get_connection() as conn:
        rows = await conn.fetch(sql, *params)
    return [CutoffOut(**dict(r)) for r in rows]


# ── GET /cutoff-trend ─────────────────────────────────────────────────────────

@app.get("/cutoff-trend", response_model=list[TrendPoint], tags=["analytics"])
async def cutoff_trend(
    institute: str = Query(...),
    program: str = Query(...),
    quota: str = Query("AI"),
    seat_type: str = Query("Gender-Neutral"),
):
    """Returns closing ranks across all available years and rounds for a
    specific institute + program combo so the frontend can plot cutoff movement.
    """
    sql = """
        SELECT year, round, closing_rank FROM cutoffs
        WHERE institute = $1 AND program = $2 AND quota = $3 AND seat_type = $4
        ORDER BY year ASC, round ASC
    """
    async with get_connection() as conn:
        rows = await conn.fetch(sql, institute, program, quota, seat_type)
    return [TrendPoint(**dict(r)) for r in rows]


# ── GET /round-progression ────────────────────────────────────────────────────

@app.get("/round-progression", response_model=list[RoundProgressionPoint], tags=["analytics"])
async def round_progression(
    institute: str = Query(...),
    program: str = Query(...),
    year: int = Query(...),
    quota: str = Query("AI"),
    seat_type: str = Query("Gender-Neutral"),
):
    """Returns round-by-round opening and closing ranks for a specific year
    so the copilot can predict R4/R5 movement from R1-R3 data.
    """
    sql = """
        SELECT round, opening_rank, closing_rank FROM cutoffs
        WHERE institute = $1 AND program = $2 AND year = $3 AND quota = $4 AND seat_type = $5
        ORDER BY round ASC
    """
    async with get_connection() as conn:
        rows = await conn.fetch(sql, institute, program, year, quota, seat_type)
    return [RoundProgressionPoint(**dict(r)) for r in rows]



# ── POST /api/save-email ─────────────────────────────────────────────────────

@app.post("/api/save-email", tags=["users"])
async def save_email(body: UserIn):
    """Store a Google-login user profile. Upserts on email so duplicates
    just bump login_count and last_login."""
    now = datetime.now(timezone.utc)
    sql = """
        INSERT INTO users (email, name, picture, login_count, first_login, last_login)
        VALUES ($1, $2, $3, 1, $4, $4)
        ON CONFLICT (email) DO UPDATE
            SET name       = COALESCE(EXCLUDED.name, users.name),
                picture    = COALESCE(EXCLUDED.picture, users.picture),
                login_count = users.login_count + 1,
                last_login  = EXCLUDED.last_login
        RETURNING id, login_count
    """
    async with get_connection() as conn:
        row = await conn.fetchrow(sql, body.email, body.name, body.picture, now)
    return {"status": "ok", "user_id": row["id"], "login_count": row["login_count"]}


# ── GET /api/emails (JSON, password-protected) ──────────────────────────────

@app.get("/api/emails", response_model=list[UserOut], tags=["users"])
async def get_emails(password: str = Query(..., description="Admin password")):
    """Return all collected user emails. Requires ?password=... query param."""
    if password != ADMIN_PASSWORD:
        raise HTTPException(status_code=403, detail="Invalid admin password")
    async with get_connection() as conn:
        rows = await conn.fetch("SELECT * FROM users ORDER BY last_login DESC")
    return [UserOut(**dict(r)) for r in rows]


# ── GET /emails (HTML dashboard, password-protected) ─────────────────────────

@app.get("/emails", response_class=HTMLResponse, tags=["users"])
async def emails_dashboard(password: str = Query(..., description="Admin password")):
    """Pretty HTML dashboard to view all collected emails."""
    if password != ADMIN_PASSWORD:
        raise HTTPException(status_code=403, detail="Invalid admin password")

    async with get_connection() as conn:
        rows = await conn.fetch("SELECT * FROM users ORDER BY last_login DESC")

    table_rows = ""
    for i, r in enumerate(rows, 1):
        pic = f'<img src="{r["picture"]}" width="32" height="32" style="border-radius:50%">' if r["picture"] else "—"
        name = r["name"] or "—"
        first = str(r["first_login"])[:19]
        last = str(r["last_login"])[:19]
        table_rows += f"""<tr>
            <td>{i}</td><td>{pic}</td><td><strong>{name}</strong></td>
            <td>{r['email']}</td><td>{r['login_count']}</td>
            <td>{first}</td><td>{last}</td>
        </tr>"""

    count = len(rows)
    return f"""<!DOCTYPE html>
<html><head><title>OviGuide — User Emails</title>
<style>
  body {{ font-family: system-ui, sans-serif; max-width: 960px; margin: 40px auto; padding: 0 20px; background: #0e0e0e; color: #F5F0E8; }}
  h1 {{ font-size: 1.6rem; margin-bottom: 4px; }}
  p {{ color: #D4CFC8; margin-bottom: 20px; }}
  table {{ width: 100%; border-collapse: collapse; }}
  th, td {{ text-align: left; padding: 10px 12px; border-bottom: 1px solid #222; }}
  th {{ color: #D4CFC8; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; }}
  tr:hover {{ background: #1a1a1a; }}
  img {{ vertical-align: middle; }}
</style></head>
<body>
  <h1>OviGuide — Collected Emails</h1>
  <p>{count} user{"s" if count != 1 else ""} logged in so far</p>
  <table>
    <tr><th>#</th><th></th><th>Name</th><th>Email</th><th>Logins</th><th>First Login</th><th>Last Login</th></tr>
    {table_rows if table_rows else '<tr><td colspan="7" style="text-align:center;color:#666;padding:40px">No logins yet</td></tr>'}
  </table>
</body></html>"""