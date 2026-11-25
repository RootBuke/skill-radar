from pathlib import Path

import psycopg

from skill_radar import config  # noqa: F401

SCHEMA_FILE = Path(__file__).with_name("schema.sql")


def connect() -> psycopg.Connection:
    return psycopg.connect()


def init_db(conn: psycopg.Connection) -> None:
    conn.execute(SCHEMA_FILE.read_text(encoding="utf-8"))
    conn.commit()
