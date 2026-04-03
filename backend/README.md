# OviGuide Cutoff API

FastAPI backend for storing and querying JoSAA counselling cutoff data.

## Quick Start

```bash
# From the repo root
cp backend/.env.example backend/.env   # edit API_KEY if desired
docker compose up --build -d
```

The API starts at **http://localhost:8000** and auto-runs Alembic migrations on boot.
Swagger docs live at **http://localhost:8000/docs**.

## Ingest Data

POST cutoff rows (e.g. from the Selenium scraper) as JSON:

```bash
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -H "X-API-Key: changeme-secret-key-123" \
  -d '{
    "rows": [
      {
        "year": 2024,
        "round": 5,
        "institute": "National Institute of Technology Warangal",
        "program": "Civil Engineering (4 Years, Bachelor of Technology)",
        "quota": "OS",
        "seat_type": "Gender-Neutral",
        "opening_rank": 20145,
        "closing_rank": 25059
      }
    ]
  }'
```

Re-running is safe — duplicates are silently skipped via `ON CONFLICT DO NOTHING`.

## Rank Check (Core Prediction)

```bash
curl "http://localhost:8000/rank-check?rank=24150&year=2024&quota=OS&seat_type=Gender-Neutral"
```

Returns all seats where `closing_rank >= 24150`, sorted by tightest cutoff first.

## Other Endpoints

| Endpoint               | Description                                      |
|------------------------|--------------------------------------------------|
| `GET /cutoffs`         | Paginated query with filters                     |
| `GET /institutes`      | Distinct institute list                          |
| `GET /programs`        | Distinct programs (optionally by institute)       |
| `GET /cutoff-trend`    | Closing ranks across years/rounds for a combo    |
| `GET /round-progression` | Round-by-round ranks for one year              |

## Environment Variables

| Variable       | Description                        |
|----------------|------------------------------------|
| `DATABASE_URL` | PostgreSQL connection string       |
| `API_KEY`      | Required header for `/ingest`      |

## Tech Stack

FastAPI · asyncpg · Pydantic v2 · Alembic · PostgreSQL 15 · Docker Compose

