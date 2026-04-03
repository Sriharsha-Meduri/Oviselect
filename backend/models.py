"""Pydantic v2 schemas for request / response validation."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ── Ingest ────────────────────────────────────────────────────────────────────

class CutoffRow(BaseModel):
    """Shape of a single cutoff row as POSTed by the scraper.

    Field names match the snake_cased JoSAA CSV columns so the scraper
    can POST rows with minimal transformation.
    """

    year: int = Field(..., ge=2015, le=2099, description="Counselling year, e.g. 2024")
    round: int = Field(..., ge=1, le=8, description="Round 1-6, 7=Special Round 1, 8=Special Round 2")
    institute: str = Field(..., min_length=1, description="Institute name exactly as in JoSAA CSV")
    academic_program_name: str = Field(..., min_length=1, alias="program", description="Program name, e.g. 'Computer Science and Engineering (4 Years)'")
    quota: str = Field(..., pattern=r"^(HS|OS|AI)$", description="HS / OS / AI")
    seat_type: str = Field(..., description="Gender-Neutral or Female-Only")
    opening_rank: Optional[int] = Field(None, ge=0, description="Opening rank (null if not available)")
    closing_rank: Optional[int] = Field(None, ge=0, description="Closing rank (null if not available)")

    model_config = {"populate_by_name": True}


class IngestRequest(BaseModel):
    rows: list[CutoffRow] = Field(..., min_length=1, max_length=50_000)


class IngestResponse(BaseModel):
    inserted: int
    skipped: int
    total: int


# ── Query responses ───────────────────────────────────────────────────────────

class CutoffOut(BaseModel):
    id: int
    year: int
    round: int
    institute: str
    program: str
    quota: str
    seat_type: str
    opening_rank: Optional[int]
    closing_rank: Optional[int]
    created_at: datetime


class PaginatedCutoffs(BaseModel):
    data: list[CutoffOut]
    total: int
    page: int
    page_size: int


class TrendPoint(BaseModel):
    year: int
    round: int
    closing_rank: Optional[int]


class RoundProgressionPoint(BaseModel):
    round: int
    opening_rank: Optional[int]
    closing_rank: Optional[int]


# ── User / Email collection ──────────────────────────────────────────────────

class UserIn(BaseModel):
    email: str
    name: Optional[str] = None
    picture: Optional[str] = None


class UserOut(BaseModel):
    id: int
    email: str
    name: Optional[str]
    picture: Optional[str]
    login_count: int
    first_login: datetime
    last_login: datetime

