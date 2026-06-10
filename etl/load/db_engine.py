"""SQLAlchemy database engine factory."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from etl.config import MySQLConfig


def build_connection_url(cfg: MySQLConfig) -> str:
    return (
        f"mysql+pymysql://{cfg.user}:{cfg.password}"
        f"@{cfg.host}:{cfg.port}/{cfg.database}?charset=utf8mb4"
    )


def create_db_engine(cfg: MySQLConfig) -> Engine:
    return create_engine(
        build_connection_url(cfg),
        pool_pre_ping=True,
        pool_recycle=3600,
        echo=False,
    )


@contextmanager
def get_connection(cfg: MySQLConfig) -> Iterator:
    engine = create_db_engine(cfg)
    conn = engine.connect()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
        engine.dispose()
