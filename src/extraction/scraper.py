"""Extraction orchestrator and pagination engine for StreamForge."""

from __future__ import annotations

import datetime
import json
import logging
import time
from pathlib import Path
from typing import Any

from config.settings import settings
from src.extraction.client import HTTPClient
from src.extraction.exporter import export_extracted_dataset
from src.extraction.fingerprint import DeduplicationIndex, generate_record_fingerprint
from src.extraction.parser import HTMLParser

logger = logging.getLogger("streamforge.extraction.scraper")


class ExtractionReport:
    """Detailed metadata report of an extraction run."""

    def __init__(self):
        self.start_time: str = datetime.datetime.now(datetime.timezone.utc).isoformat()
        self.end_time: str = ""
        self.elapsed_seconds: float = 0.0
        self.is_offline_run: bool = False
        self.starting_url: str = ""
        self.pages_visited: list[str] = []
        self.successful_requests: int = 0
        self.failed_pages: list[dict[str, Any]] = []
        self.records_extracted_total: int = 0
        self.duplicates_removed: int = 0
        self.unique_records_retained: int = 0
        self.export_metadata: dict[str, Any] = {}

    def finish(self, elapsed: float, exports: dict[str, Any]) -> None:
        self.end_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
        self.elapsed_seconds = round(elapsed, 3)
        self.export_metadata = exports

    def to_dict(self) -> dict[str, Any]:
        return {
            "start_time": self.start_time,
            "end_time": self.end_time,
            "elapsed_seconds": self.elapsed_seconds,
            "is_offline_run": self.is_offline_run,
            "starting_url": self.starting_url,
            "pages_visited_count": len(self.pages_visited),
            "pages_visited": self.pages_visited,
            "successful_requests": self.successful_requests,
            "failed_pages_count": len(self.failed_pages),
            "failed_pages": self.failed_pages,
            "records_extracted_total": self.records_extracted_total,
            "duplicates_removed": self.duplicates_removed,
            "unique_records_retained": self.unique_records_retained,
            "exports": self.export_metadata,
        }

    def save(self, target_path: Path | None = None) -> Path:
        path = target_path or (settings.REPORTS_DIR / "extraction_report.json")
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)
        logger.info(f"Extraction report saved to {path}")
        return path


class StreamForgeScraper:
    """Configurable web scraper processing paginated live or offline HTML pages."""

    def __init__(
        self,
        base_url: str | None = None,
        max_pages: int | None = None,
        record_limit: int | None = None,
        delay_sec: float | None = None,
        is_offline: bool = False,
    ):
        self.is_offline = is_offline
        self.base_url = base_url or ("page_1.html" if is_offline else "https://forge-jobs.internal/listings")
        self.max_pages = max_pages or settings.SCRAPER_MAX_PAGES
        self.record_limit = record_limit or settings.SCRAPER_MAX_RECORDS
        self.delay_sec = delay_sec if delay_sec is not None else (0.0 if is_offline else settings.SCRAPER_DEFAULT_DELAY_SEC)

        self.client = HTTPClient(delay_sec=self.delay_sec)
        self.parser = HTMLParser(base_url=self.base_url)
        self.dedup_index = DeduplicationIndex()

    def run(self, start_url: str | None = None) -> tuple[list[dict[str, Any]], ExtractionReport]:
        """Execute the extraction run traversing pagination links until limits are reached."""
        current_url = start_url or self.base_url
        report = ExtractionReport()
        report.starting_url = current_url
        report.is_offline_run = self.is_offline

        unique_records: list[dict[str, Any]] = []
        page_count = 0
        start_clock = time.perf_counter()

        logger.info(f"Starting extraction run: start_url={current_url}, offline={self.is_offline}, max_pages={self.max_pages}")

        while current_url and page_count < self.max_pages and len(unique_records) < self.record_limit:
            page_count += 1
            report.pages_visited.append(current_url)

            response = self.client.fetch(current_url, is_offline=self.is_offline)

            if not response.is_success:
                logger.error(f"Failed to fetch {current_url}: {response.error_message}")
                report.failed_pages.append({
                    "url": current_url,
                    "status_code": response.status_code,
                    "error": response.error_message,
                })
                break

            report.successful_requests += 1

            # Parse page
            page_records, next_url = self.parser.parse_page(response.text, current_url=current_url)
            report.records_extracted_total += len(page_records)

            for rec in page_records:
                fingerprint = generate_record_fingerprint(rec)
                rec["fingerprint_hash"] = fingerprint

                if self.dedup_index.add(fingerprint):
                    unique_records.append(rec)
                    if len(unique_records) >= self.record_limit:
                        logger.info(f"Reached record limit ({self.record_limit}). Halting extraction.")
                        break
                else:
                    report.duplicates_removed += 1

            current_url = next_url

        elapsed = time.perf_counter() - start_clock
        report.unique_records_retained = len(unique_records)

        # Export outputs
        export_meta = export_extracted_dataset(unique_records)
        report.finish(elapsed, export_meta)
        report.save()

        logger.info(
            f"Extraction completed in {elapsed:.2f}s: "
            f"{report.records_extracted_total} raw records, "
            f"{report.duplicates_removed} duplicates dropped, "
            f"{report.unique_records_retained} unique records saved."
        )

        return unique_records, report
