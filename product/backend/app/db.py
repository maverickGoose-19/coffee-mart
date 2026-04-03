from __future__ import annotations

import logging
from contextlib import contextmanager

from psycopg.rows import dict_row

try:
    from psycopg_pool import ConnectionPool
except ImportError as _exc:
    raise ImportError(
        "psycopg_pool is required. Run: pip install 'psycopg[pool]'  "
        "(or: pip install psycopg-pool)"
    ) from _exc

from .config import settings

logger = logging.getLogger(__name__)

_pool: ConnectionPool | None = None


def _build_conninfo() -> str:
    db_url = settings.supabase_db_url
    if "sslmode=" not in db_url:
        separator = "&" if "?" in db_url else "?"
        db_url = f"{db_url}{separator}sslmode=require"
    return db_url


def get_pool() -> ConnectionPool:
    """Return (and lazily open) the module-level connection pool."""
    global _pool
    if _pool is None:
        _pool = ConnectionPool(
            conninfo=_build_conninfo(),
            min_size=1,
            max_size=10,
            open=False,
        )
        _pool.open()
        logger.info("DB connection pool opened (min=1, max=10)")
    return _pool


def close_pool() -> None:
    """Close the pool on application shutdown."""
    global _pool
    if _pool is not None:
        _pool.close()
        _pool = None
        logger.info("DB connection pool closed")


@contextmanager
def _connection():
    """Yield a pooled connection; commits on success, rolls back on error."""
    with get_pool().connection() as conn:
        yield conn


def query_all(sql: str, params: tuple | dict | None = None) -> list[dict]:
    with _connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(sql, params or ())
            return list(cur.fetchall())


def query_one(sql: str, params: tuple | dict | None = None) -> dict | None:
    rows = query_all(sql, params)
    return rows[0] if rows else None


def execute(sql: str, params: tuple | dict | None = None) -> None:
    with _connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
        # ConnectionPool's context manager auto-commits on clean exit.
