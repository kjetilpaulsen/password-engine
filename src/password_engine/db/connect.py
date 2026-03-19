from __future__ import annotations

import logging
import os

from password_engine.runtime.runtime import CFGDataBase
import psycopg
# import psycopg.sql

logger = logging.getLogger(__name__)


def connect(settings: CFGDataBase | None = None) -> psycopg.Connection:
    """
    Creates a psycopg connection using explicit settings or env defaults

    Params:
    - settings: optional explicit dbsettings. If omitted values are constructed
    from env variable with module defaults as fallback

    Returns:
    - psycopg.Connection: a new database connection with autocommit disabled
    """
    logger.debug("Start ..")
    s = settings or CFGDataBase(
        db_host=os.getenv("DB_HOST", "/run/postgresql"),
        db_name=os.getenv("DB_NAME", "market_analysis_engine"),
        db_user=os.getenv("DB_USER") or None,
        db_password=os.getenv("DB_PASSWORD") or None,
        db_port=int(os.getenv("DB_PORT", "5432")),
    )

    logger.debug("End ..")

    return psycopg.connect(
        dbname=s.db_name,
        host=s.db_host,
        user=s.db_user,
        password=s.db_password,
        port=s.db_port,
        autocommit=False,
    )
