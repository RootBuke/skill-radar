"""EXTRACT: download job postings from the Arbeitnow API and save every page untouched.

Why files? Keeping the raw responses lets us re-process history without calling the API
again, and lets us see exactly what the source sent when something looks wrong.
"""

import logging
import time
from datetime import UTC, datetime
from pathlib import Path

import httpx
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential

from skill_radar import config

log = logging.getLogger(__name__)

USER_AGENT = "skill-radar/0.1 (student portfolio project)"
RETRY_STATUS = {429, 500, 502, 503, 504}


def _is_retryable(exc: BaseException) -> bool:
    """Retry network hiccups and server-side errors, never client errors like 404."""
    if isinstance(exc, httpx.TransportError):
        return True
    return isinstance(exc, httpx.HTTPStatusError) and exc.response.status_code in RETRY_STATUS


@retry(
    retry=retry_if_exception(_is_retryable),
    stop=stop_after_attempt(4),
    wait=wait_exponential(multiplier=2, max=30),
    reraise=True,
)
def fetch_page(client: httpx.Client, url: str) -> httpx.Response:
    response = client.get(url)
    response.raise_for_status()
    return response


def extract(
    max_pages: int = 3,
    pause: float = 1.0,
    out_dir: Path | None = None,
    url: str | None = None,
    client: httpx.Client | None = None,
) -> Path:
    """Download up to `max_pages` pages into a new batch folder and return that folder."""
    batch_dir = (out_dir or config.RAW_DIR) / datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    batch_dir.mkdir(parents=True, exist_ok=True)

    owns_client = client is None
    client = client or httpx.Client(
        headers={"User-Agent": USER_AGENT}, timeout=30, follow_redirects=True
    )
    next_url = url or config.API_URL
    try:
        for page in range(1, max_pages + 1):
            response = fetch_page(client, next_url)
            (batch_dir / f"page_{page:04d}.json").write_bytes(response.content)
            body = response.json()
            jobs = body.get("data", [])
            log.info("page %d: %d postings", page, len(jobs))
            next_url = (body.get("links") or {}).get("next")
            if not jobs or not next_url:
                break
            time.sleep(pause)  # be polite: the API is free, so do not hammer it
    finally:
        if owns_client:
            client.close()
    return batch_dir
