"""Run the API → Python → PostgreSQL ETL pipeline."""

import logging
from pathlib import Path

from dotenv import load_dotenv

from src.api_client import fetch_resource
from src.database import create_tables, get_engine, get_table_counts, load_posts, load_users
from src.transform import transform_posts, transform_users

load_dotenv()

ROOT = Path(__file__).resolve().parent.parent
LOG_DIR = ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

LOG_LEVEL = __import__("os").getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_DIR / "pipeline.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger("pipeline")


def run_pipeline() -> None:
    logger.info("Starting API → Python → PostgreSQL pipeline")
    engine = get_engine()

    try:
        create_tables(engine)

        raw_users = fetch_resource("users")
        raw_posts = fetch_resource("posts")

        users_df = transform_users(raw_users)
        valid_user_ids = set(users_df["id"].astype(int).tolist()) if not users_df.empty else set()
        posts_df = transform_posts(raw_posts, valid_user_ids)

        loaded_users = load_users(engine, users_df)
        loaded_posts = load_posts(engine, posts_df)

        counts = get_table_counts(engine)
        logger.info("Run completed successfully")
        logger.info("Records processed this run: users=%s, posts=%s", loaded_users, loaded_posts)
        logger.info("Total rows in database: users=%s, posts=%s", counts["users"], counts["posts"])
    except Exception:
        logger.exception("Pipeline failed")
        raise
    finally:
        engine.dispose()


if __name__ == "__main__":
    run_pipeline()
