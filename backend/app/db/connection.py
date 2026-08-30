"""
Database Connection & Pool Management
=====================================
Provides connection pooling and connection management for Prisma Postgres via psycopg3.
"""

from __future__ import annotations

import logging
from contextlib import contextmanager
from typing import Generator

import psycopg
from psycopg_pool import ConnectionPool

from app.config import settings

logger = logging.getLogger("migrantaid")

_pool: ConnectionPool | None = None


def init_db_pool() -> ConnectionPool | None:
    """Initialize the database connection pool if DATABASE_URL is configured."""
    global _pool  # noqa: PLW0603
    db_url = settings.DATABASE_URL
    if not db_url:
        logger.warning("DATABASE_URL is not set. Database persistence will be unavailable.")
        return None

    try:
        if _pool is None:
            logger.info("Initializing database connection pool...")
            _pool = ConnectionPool(
                conninfo=db_url,
                min_size=1,
                max_size=10,
                kwargs={"autocommit": True},
                open=True,
            )
            logger.info("Database connection pool initialized successfully.")
        return _pool
    except Exception as e:
        logger.error(f"Failed to initialize database connection pool: {e!s}")
        _pool = None
        return None


def close_db_pool() -> None:
    """Close the database connection pool."""
    global _pool  # noqa: PLW0603
    if _pool is not None:
        try:
            logger.info("Closing database connection pool...")
            _pool.close()
            logger.info("Database connection pool closed.")
        except Exception as e:
            logger.error(f"Error closing database connection pool: {e!s}")
        finally:
            _pool = None


@contextmanager
def get_db_connection() -> Generator[psycopg.Connection, None, None]:
    """
    Context manager for obtaining a database connection.
    Uses pool if available, otherwise opens a direct connection.
    """
    db_url = settings.DATABASE_URL
    if not db_url:
        raise RuntimeError("DATABASE_URL is not configured.")

    if _pool is not None:
        with _pool.connection() as conn:
            yield conn
    else:
        with psycopg.connect(db_url, autocommit=True) as conn:
            yield conn


def check_db_connection() -> bool:
    """Check database health by running a simple query."""
    if not settings.DATABASE_URL:
        return False
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1;")
                return True
    except Exception as e:
        logger.warning(f"Database health check failed: {e!s}")
        return False
