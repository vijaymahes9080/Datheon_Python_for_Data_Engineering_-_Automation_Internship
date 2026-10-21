"""Unit tests for Task 1: Autonomous Web Scraper & Extractor."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest

from src.extraction.client import HTTPClient
from src.extraction.exporter import export_to_csv, export_to_json
from src.extraction.fingerprint import (
    canonicalize_text,
    canonicalize_url,
    DeduplicationIndex,
    generate_record_fingerprint,
)
from src.extraction.parser import HTMLParser
from src.extraction.scraper import StreamForgeScraper


class TestHTMLParser:
    """Tests for HTML parsing logic."""

    def test_parse_complete_job_card(self, sample_card_html: str):
        parser = HTMLParser(base_url="https://example.com")
        records, next_url = parser.parse_page(sample_card_html)

        assert len(records) == 1
        rec = records[0]
        assert rec["job_title"] == "Lead Systems Architect"
        assert rec["company_name"] == "Apex Systems"
        assert rec["salary_raw"] == "$160,000 - $190,000"
        assert rec["location"] == "Remote (US)"
        assert rec["category"] == "Cloud Systems"
        assert rec["employment_type"] == "Full-time"
        assert rec["posted_date_raw"] == "2026-10-21"
        assert rec["source_url"] == "https://example.com/jobs/999"
        assert next_url is None

    def test_parse_missing_elements_gracefully(self, messy_card_html: str):
        parser = HTMLParser(base_url="https://example.com/test")
        records, _ = parser.parse_page(messy_card_html, current_url="https://example.com/test")

        assert len(records) == 1
        rec = records[0]
        assert rec["job_title"] == "Incomplete Listing"
        assert rec["company_name"] == ""
        assert rec["salary_raw"] == "Unspecified"
        assert rec["location"] == "Unspecified"
        assert rec["category"] == "General"

    def test_pagination_link_extraction(self):
        html = """
        <div>
          <article class="job-card"><h2>Job 1</h2></article>
          <a class="pagination-next" href="/listings?page=2">Next Page</a>
        </div>
        """
        parser = HTMLParser(base_url="https://example.com")
        _, next_url = parser.parse_page(html, current_url="https://example.com/listings?page=1")
        assert next_url == "https://example.com/listings?page=2"


class TestFingerprintAndDeduplication:
    """Tests for canonical hashing and deduplication."""

    def test_canonicalize_text(self):
        assert canonicalize_text("  Senior   Software   Engineer  ") == "senior software engineer"
        assert canonicalize_text(None) == ""

    def test_canonicalize_url(self):
        assert canonicalize_url("HTTPS://Example.COM/Jobs/123/?ref=feed#anchor") == "https://example.com/Jobs/123?ref=feed"

    def test_fingerprint_deterministic(self):
        rec_a = {"job_title": "Data Engineer", "company_name": "Apex", "source_url": "https://example.com/1"}
        rec_b = {"job_title": "  Data  Engineer ", "company_name": "APEX", "source_url": "https://example.com/1/"}
        assert generate_record_fingerprint(rec_a) == generate_record_fingerprint(rec_b)

    def test_deduplication_index(self):
        idx = DeduplicationIndex()
        assert idx.add("hash_1") is True
        assert idx.add("hash_2") is True
        assert idx.add("hash_1") is False  # Duplicate
        assert idx.duplicates_count == 1
        assert idx.total_unique == 2


class TestHTTPClient:
    """Tests for network client and bounded retries."""

    def test_offline_fixture_fetch(self, html_fixtures_dir: Path):
        client = HTTPClient(delay_sec=0.0)
        res = client.fetch("page_1.html", is_offline=True)
        assert res.is_success is True
        assert res.status_code == 200
        assert "StreamForge Technical Job Board" in res.text

    def test_offline_fixture_not_found(self):
        client = HTTPClient(delay_sec=0.0)
        res = client.fetch("non_existent_page.html", is_offline=True)
        assert res.is_success is False
        assert res.status_code == 404

    @patch("requests.Session.get")
    def test_retry_on_503_recoverable(self, mock_get):
        # First attempt 503, second attempt 200
        resp_503 = MagicMock(status_code=503)
        resp_200 = MagicMock(status_code=200, text="<html>Success</html>", url="https://example.com")
        mock_get.side_effect = [resp_503, resp_200]

        client = HTTPClient(max_retries=2, backoff_factor=0.01, delay_sec=0.0)
        res = client.fetch("https://example.com")
        assert res.is_success is True
        assert res.status_code == 200
        assert mock_get.call_count == 2


class TestExporters:
    """Tests for CSV and JSON file exports."""

    def test_export_csv_and_json(self, tmp_path: Path):
        records = [
            {"job_title": "Data Analyst", "company_name": "Quant Co", "salary_raw": "$90k"},
            {"job_title": "Backend Dev", "company_name": "Cloud Co", "salary_raw": "$120k"},
        ]
        csv_file = tmp_path / "test.csv"
        json_file = tmp_path / "test.json"

        export_to_csv(records, target_path=csv_file)
        export_to_json(records, target_path=json_file)

        assert csv_file.exists()
        assert json_file.exists()
        
        with open(json_file, encoding="utf-8") as f:
            data = json.load(f)
        assert len(data) == 2
        assert data[0]["job_title"] == "Data Analyst"


class TestFullOfflineExtractionRun:
    """Integration test verifying extraction of 100+ unique records."""

    def test_offline_extraction_reaches_100_records(self):
        scraper = StreamForgeScraper(
            base_url="page_1.html",
            max_pages=3,
            record_limit=150,
            delay_sec=0.0,
            is_offline=True,
        )
        records, report = scraper.run()

        assert len(records) >= 100
        assert report.unique_records_retained >= 100
        assert report.successful_requests == 3
        assert report.duplicates_removed == 0
        assert report.failed_pages == []
