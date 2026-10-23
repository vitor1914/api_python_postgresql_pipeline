"""PostgreSQL schema creation and idempotent data loading."""

import logging
import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

load_dotenv()
logger = logging.getLogger(__name__)


def get_engine() -> Engine:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is not configured. Check your .env file.")
    return create_engine(database_url, pool_pre_ping=True, future=True)


def create_tables(engine: Engine) -> None:
    """Create target tables when they do not exist."""
    statements = [
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            username TEXT,
            email TEXT,
            city TEXT,
            company TEXT,
            loaded_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id),
            title TEXT NOT NULL,
            body TEXT,
            loaded_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """,
        "CREATE INDEX IF NOT EXISTS idx_posts_user_id ON posts(user_id)",
    ]
    with engine.begin() as connection:
        for statement in statements:
            connection.execute(text(statement))
    logger.info("Database tables and indexes are ready")


def _upsert_dataframe(engine: Engine, table: str, df: pd.DataFrame, columns: list[str]) -> int:
    """Upsert DataFrame rows using PostgreSQL conflict handling."""
    if df.empty:
        logger.warning("No records to load into %s", table)
        return 0

    allowed_tables = {"users", "posts"}
    if table not in allowed_tables:
        raise ValueError("Unsupported target table")

    update_columns = [column for column in columns if column != "id"]
    insert_columns = ", ".join(columns)
    placeholders = ", ".join(f":{column}" for column in columns)
    updates = ", ".join(f"{column} = EXCLUDED.{column}" for column in update_columns)
    sql = text(
        f"INSERT INTO {table} ({insert_columns}) VALUES ({placeholders}) "
        f"ON CONFLICT (id) DO UPDATE SET {updates}, loaded_at = CURRENT_TIMESTAMP"
    )

    records = df[columns].where(pd.notna(df[columns]), None).to_dict(orient="records")
    with engine.begin() as connection:
        connection.execute(sql, records)

    logger.info("Loaded/upserted %s rows into %s", len(records), table)
    return len(records)


def load_users(engine: Engine, df: pd.DataFrame) -> int:
    return _upsert_dataframe(
        engine, "users", df,
        ["id", "name", "username", "email", "city", "company"],
    )


def load_posts(engine: Engine, df: pd.DataFrame) -> int:
    return _upsert_dataframe(engine, "posts", df, ["id", "user_id", "title", "body"])


def get_table_counts(engine: Engine) -> dict[str, int]:
    with engine.connect() as connection:
        users = connection.execute(text("SELECT COUNT(*) FROM users")).scalar_one()
        posts = connection.execute(text("SELECT COUNT(*) FROM posts")).scalar_one()
    return {"users": users, "posts": posts}
