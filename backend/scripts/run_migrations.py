"""
Database Migration Execution Script
===================================
Applies SQL schema migrations to Prisma Postgres database using DIRECT_URL or DATABASE_URL.
"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

import psycopg

# Ensure project root is in sys.path
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.config import settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("migrations")


def run_migrations() -> bool:
    target_url = settings.DIRECT_URL or settings.DATABASE_URL
    if not target_url:
        logger.error("Neither DIRECT_URL nor DATABASE_URL is set in environment.")
        return False

    migrations_dir = PROJECT_ROOT / "app" / "db" / "migrations"
    sql_files = sorted(migrations_dir.glob("*.sql"))

    if not sql_files:
        logger.warning(f"No SQL migration files found in {migrations_dir}")
        return True

    logger.info(f"Connecting to database to apply {len(sql_files)} migration file(s)...")

    try:
        with psycopg.connect(target_url, autocommit=True) as conn:
            with conn.cursor() as cur:
                for sql_file in sql_files:
                    logger.info(f"Executing migration: {sql_file.name}")
                    sql_content = sql_file.read_text(encoding="utf-8")
                    cur.execute(sql_content)
                    logger.info(f"Successfully applied {sql_file.name}")
        logger.info("All migrations completed successfully!")
        return True
    except Exception as e:
        logger.error(f"Migration execution failed: {e!s}")
        return False


if __name__ == "__main__":
    success = run_migrations()
    sys.exit(0 if success else 1)
