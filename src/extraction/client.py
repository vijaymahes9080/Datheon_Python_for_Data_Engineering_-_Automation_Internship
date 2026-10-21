"""HTTP client module with exponential backoff retries and offline fixture support."""

from __future__ import annotations

import logging
import random
import time
from pathlib import Path
from typing import Any
import requests

from config.settings import settings

logger = logging.getLogger("streamforge.extraction.client")


class HTTPClientResponse:
    """Standardized response container for network and offline requests."""

    def __init__(
        self,
        status_code: int,
        text: str,
        url: str,
        elapsed_seconds: float = 0.0,
        is_success: bool = True,
        error_message: str | None = None,
    ):
        self.status_code = status_code
        self.text = text
        self.url = url
        self.elapsed_seconds = elapsed_seconds
        self.is_success = is_success
        self.error_message = error_message

    def __repr__(self) -> str:
        return f"<HTTPClientResponse status={self.status_code} url='{self.url}' success={self.is_success}>"


class HTTPClient:
    """Configurable HTTP client supporting session pooling, exponential backoff retries,

    and transparent local offline HTML fixture fallback.
    """

    RECOVERABLE_STATUS_CODES = {429, 500, 502, 503, 504}

    def __init__(
        self,
        user_agent: str | None = None,
        timeout_sec: int | None = None,
        max_retries: int | None = None,
        backoff_factor: float | None = None,
        delay_sec: float | None = None,
    ):
        self.user_agent = user_agent or settings.SCRAPER_USER_AGENT
        self.timeout_sec = timeout_sec or settings.SCRAPER_REQUEST_TIMEOUT_SEC
        self.max_retries = max_retries if max_retries is not None else settings.SCRAPER_MAX_RETRIES
        self.backoff_factor = backoff_factor or settings.SCRAPER_BACKOFF_FACTOR
        self.delay_sec = delay_sec if delay_sec is not None else settings.SCRAPER_DEFAULT_DELAY_SEC
        
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        })

    def fetch(self, url: str, params: dict[str, Any] | None = None, is_offline: bool = False) -> HTTPClientResponse:
        """Fetch URL with bounded retries and exponential backoff, or load offline fixture.

        Args:
            url: The target HTTP URL, file:// URI, or relative fixture filename.
            params: Optional query parameters.
            is_offline: If True or url starts with file://, resolves locally.

        Returns:
            HTTPClientResponse containing status, text, duration, and error details.
        """
        # Pacing delay between requests to respect rate limits
        if self.delay_sec > 0 and not is_offline:
            time.sleep(self.delay_sec)

        # Handle offline mode or local files
        if is_offline or url.startswith("file://") or not url.startswith(("http://", "https://")):
            return self._fetch_offline(url)

        attempt = 0
        last_error = ""

        while attempt < self.max_retries:
            attempt += 1
            start_time = time.perf_counter()
            try:
                logger.info(f"Fetching URL (attempt {attempt}/{self.max_retries}): {url}")
                response = self.session.get(url, params=params, timeout=self.timeout_sec)
                elapsed = time.perf_counter() - start_time

                if response.status_code == 200:
                    return HTTPClientResponse(
                        status_code=200,
                        text=response.text,
                        url=response.url,
                        elapsed_seconds=elapsed,
                        is_success=True,
                    )

                if response.status_code in self.RECOVERABLE_STATUS_CODES:
                    last_error = f"HTTP {response.status_code}: Recoverable server response."
                    logger.warning(f"Recoverable error for {url}: {last_error}")
                else:
                    logger.error(f"Unrecoverable HTTP {response.status_code} for {url}")
                    return HTTPClientResponse(
                        status_code=response.status_code,
                        text=response.text,
                        url=response.url,
                        elapsed_seconds=elapsed,
                        is_success=False,
                        error_message=f"HTTP {response.status_code}: Non-recoverable error",
                    )

            except (requests.Timeout, requests.ConnectionError) as exc:
                elapsed = time.perf_counter() - start_time
                last_error = f"Network error ({exc.__class__.__name__}): {exc}"
                logger.warning(f"Attempt {attempt} failed for {url}: {last_error}")

            except requests.RequestException as exc:
                elapsed = time.perf_counter() - start_time
                logger.error(f"Fatal request exception for {url}: {exc}")
                return HTTPClientResponse(
                    status_code=0,
                    text="",
                    url=url,
                    elapsed_seconds=elapsed,
                    is_success=False,
                    error_message=str(exc),
                )

            # Compute exponential backoff with jitter
            if attempt < self.max_retries:
                sleep_duration = (self.backoff_factor ** attempt) + random.uniform(0.1, 0.5)
                logger.info(f"Backing off for {sleep_duration:.2f}s before retry {attempt + 1}...")
                time.sleep(sleep_duration)

        return HTTPClientResponse(
            status_code=0,
            text="",
            url=url,
            elapsed_seconds=0.0,
            is_success=False,
            error_message=f"Exhausted {self.max_retries} attempts. Last error: {last_error}",
        )

    def _fetch_offline(self, path_or_url: str) -> HTTPClientResponse:
        """Resolve content from local bundled HTML fixtures."""
        clean_path = path_or_url.replace("file://", "")
        target_path = Path(clean_path)

        # If not absolute, search in settings.HTML_FIXTURES_DIR
        if not target_path.is_absolute() or not target_path.exists():
            candidate = settings.HTML_FIXTURES_DIR / target_path.name
            if candidate.exists():
                target_path = candidate
            elif (settings.HTML_FIXTURES_DIR / clean_path).exists():
                target_path = settings.HTML_FIXTURES_DIR / clean_path

        if not target_path.exists():
            logger.error(f"Offline HTML fixture not found at {target_path}")
            return HTTPClientResponse(
                status_code=404,
                text="",
                url=str(target_path),
                is_success=False,
                error_message=f"Fixture not found: {target_path}",
            )

        try:
            start_time = time.perf_counter()
            content = target_path.read_text(encoding="utf-8")
            elapsed = time.perf_counter() - start_time
            logger.info(f"Loaded offline fixture ({len(content)} bytes) from {target_path.name}")
            return HTTPClientResponse(
                status_code=200,
                text=content,
                url=str(target_path.resolve()),
                elapsed_seconds=elapsed,
                is_success=True,
            )
        except Exception as exc:
            logger.error(f"Failed to read offline fixture {target_path}: {exc}")
            return HTTPClientResponse(
                status_code=500,
                text="",
                url=str(target_path),
                is_success=False,
                error_message=str(exc),
            )
