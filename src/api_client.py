"""HTTP client for the public JSONPlaceholder API."""

import logging
import os
from typing import Any

import requests
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

BASE_URL = os.getenv("API_BASE_URL", "https://jsonplaceholder.typicode.com").rstrip("/")
TIMEOUT = int(os.getenv("API_TIMEOUT", "30"))


def fetch_resource(resource: str) -> list[dict[str, Any]]:
    """Fetch a collection from the API and validate the response shape."""
    if resource not in {"users", "posts"}:
        raise ValueError(f"Unsupported API resource: {resource}")

    url = f"{BASE_URL}/{resource}"
    logger.info("Requesting API resource: %s", url)

    try:
        response = requests.get(url, timeout=TIMEOUT)
        response.raise_for_status()
        payload = response.json()
    except requests.RequestException as exc:
        logger.exception("API request failed for %s", resource)
        raise RuntimeError(f"API request failed for {resource}") from exc
    except ValueError as exc:
        logger.exception("API returned invalid JSON for %s", resource)
        raise RuntimeError(f"Invalid JSON received for {resource}") from exc

    if not isinstance(payload, list):
        raise TypeError(f"Expected a JSON array for {resource}")

    if not all(isinstance(item, dict) for item in payload):
        raise TypeError(f"Expected each {resource} item to be a JSON object")

    logger.info("Fetched %s records from %s", len(payload), resource)
    return payload
