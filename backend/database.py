"""Async PostgreSQL connection pool using asyncpg."""

from __future__ import annotations

import os
from contextlib import asynccontextmanager
from typing import AsyncIterator

import asyncpg
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://oviguide:oviguide_secret@db:5432/oviguide")

_pool: asyncpg.Pool | None = None


async def get_pool() -> asyncpg.Pool:
    """Return the global connection pool, creating it on first call."""
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(
            DATABASE_URL,
            min_size=2,
            max_size=20,
            command_timeout=30,
        )
    return _pool


async def close_pool() -> None:
    """Gracefully close the pool."""
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None


@asynccontextmanager
async def get_connection() -> AsyncIterator[asyncpg.Connection]:
    """Context manager that checks out a connection from the pool."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        yield conn

