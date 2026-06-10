"""MySQL connection via SQLAlchemy + PyMySQL."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

import pymysql.cursors

from etl.config import MySQLConfig
from etl.load.db_engine import create_db_engine


@contextmanager
def mysql_connection(cfg: MySQLConfig) -> Iterator:
    """Yield a PyMySQL DBAPI connection from SQLAlchemy engine."""
    engine = create_db_engine(cfg)
    conn = engine.raw_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
        engine.dispose()


def dict_cursor(conn):
    """Create a dictionary cursor compatible with loader code."""
    return conn.cursor(pymysql.cursors.DictCursor)
