"""Data cleaning and validation functions."""

import logging
from typing import Any

import pandas as pd

logger = logging.getLogger(__name__)


def _clean_text(value: Any) -> str | None:
    if value is None:
        return None
    cleaned = str(value).strip()
    return cleaned or None


def transform_users(records: list[dict[str, Any]]) -> pd.DataFrame:
    """Normalize user records into the target users schema."""
    rows = []
    rejected = 0

    for record in records:
        try:
            user_id = int(record["id"])
            name = _clean_text(record.get("name"))
            username = _clean_text(record.get("username"))
            email = _clean_text(record.get("email"))
            address = record.get("address") or {}
            company = record.get("company") or {}

            if user_id <= 0 or not name:
                raise ValueError("Missing positive ID or name")

            rows.append({
                "id": user_id,
                "name": name,
                "username": username,
                "email": email,
                "city": _clean_text(address.get("city")) if isinstance(address, dict) else None,
                "company": _clean_text(company.get("name")) if isinstance(company, dict) else None,
            })
        except (KeyError, TypeError, ValueError):
            rejected += 1

    df = pd.DataFrame(rows, columns=["id", "name", "username", "email", "city", "company"])
    if not df.empty:
        df = df.drop_duplicates(subset=["id"], keep="last")
    logger.info("Users transformed: %s accepted, %s rejected", len(df), rejected)
    return df


def transform_posts(records: list[dict[str, Any]], valid_user_ids: set[int]) -> pd.DataFrame:
    """Normalize posts and reject records with invalid or unknown user references."""
    rows = []
    rejected = 0

    for record in records:
        try:
            post_id = int(record["id"])
            user_id = int(record["userId"])
            title = _clean_text(record.get("title"))
            body = _clean_text(record.get("body"))

            if post_id <= 0 or user_id not in valid_user_ids or not title:
                raise ValueError("Invalid ID, user reference, or title")

            rows.append({
                "id": post_id,
                "user_id": user_id,
                "title": title,
                "body": body,
            })
        except (KeyError, TypeError, ValueError):
            rejected += 1

    df = pd.DataFrame(rows, columns=["id", "user_id", "title", "body"])
    if not df.empty:
        df = df.drop_duplicates(subset=["id"], keep="last")
    logger.info("Posts transformed: %s accepted, %s rejected", len(df), rejected)
    return df
