"""Unit tests for Task 2: Automated Data Cleaning & Schema Transformation."""

from __future__ import annotations

import datetime
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

from src.quality.cleaner import DataCleaner, to_snake_case
from src.quality.parsers import parse_and_normalize_date, parse_salary_and_currency
from src.quality.profiler import QualityProfiler
from src.quality.validator import SchemaValidator


class TestDataCleaner:
    """Tests for header standardization and text trimming."""

    def test_to_snake_case(self):
        assert to_snake_case("Job Title") == "job_title"
        assert to_snake_case("Salary / Compensation") == "salary_compensation"
        assert to_snake_case("Location (City/Country)") == "location_city_country"
        assert to_snake_case("posted-date-raw") == "posted_date_raw"

    def test_cleaner_headers_and_whitespace(self):
        df = pd.DataFrame({
            "Job Title": ["  Senior Engineer  ", "Lead Architect", "   "],
            "Salary / Compensation": ["$120k", "€90k", None],
        })
        cleaned_df, meta = DataCleaner.clean(df)

        assert "job_title" in cleaned_df.columns
        assert "salary_raw" in cleaned_df.columns
        assert cleaned_df["job_title"].iloc[0] == "Senior Engineer"
        # Whitespace-only string converted to None / NaN
        assert pd.isna(cleaned_df["job_title"].iloc[2])


class TestCurrencyParser:
    """Tests for currency and salary range parsing."""

    def test_range_parsing(self):
        res = parse_salary_and_currency("$140,000 - $175,000")
        assert res["currency"] == "USD"
        assert res["salary_min"] == 140000.0
        assert res["salary_max"] == 175000.0
        assert res["salary_avg"] == 157500.0

    def test_single_amount_euro(self):
        res = parse_salary_and_currency("€95,000")
        assert res["currency"] == "EUR"
        assert res["salary_min"] == 95000.0
        assert res["salary_max"] == 95000.0
        assert res["salary_avg"] == 95000.0

    def test_k_suffix_gbp(self):
        res = parse_salary_and_currency("GBP 85k - 105k")
        assert res["currency"] == "GBP"
        assert res["salary_min"] == 85000.0
        assert res["salary_max"] == 105000.0

    def test_indian_rupees_commas(self):
        res = parse_salary_and_currency("₹25,00,000 - ₹35,00,000")
        assert res["currency"] == "INR"
        assert res["salary_min"] == 2500000.0
        assert res["salary_max"] == 3500000.0

    def test_unparseable_salary_retained(self):
        res = parse_salary_and_currency("Competitive & Performance Bonus")
        assert res["salary_min"] is None
        assert res["salary_max"] is None
        assert res["salary_raw"] == "Competitive & Performance Bonus"


class TestDateParser:
    """Tests for date parsing, relative parsing, and invalid date isolation."""

    def test_iso_date(self):
        iso_str, is_valid, _ = parse_and_normalize_date("2026-10-15")
        assert is_valid is True
        assert iso_str == "2026-10-15"

    def test_european_date(self):
        iso_str, is_valid, _ = parse_and_normalize_date("18/10/2026")
        assert is_valid is True
        assert iso_str == "2026-10-18"

    def test_relative_date(self):
        ref = datetime.date(2026, 10, 21)
        iso_str, is_valid, _ = parse_and_normalize_date("2 days ago", reference_date=ref)
        assert is_valid is True
        assert iso_str == "2026-10-19"

    def test_invalid_date_caught_not_silent(self):
        iso_str, is_valid, reason = parse_and_normalize_date("CORRUPTED_DATE_TEXT")
        assert is_valid is False
        assert iso_str is None
        assert "Unparseable" in reason

    def test_future_date_rejected(self):
        ref = datetime.date(2026, 10, 21)
        iso_str, is_valid, reason = parse_and_normalize_date("2030-01-01", reference_date=ref)
        assert is_valid is False
        assert "Future date violation" in reason


class TestSchemaValidationAndRejection:
    """Tests for schema validation, rejection logging, and deduplication."""

    def test_valid_record_accepted(self):
        row = {
            "job_title": "Lead Data Engineer",
            "company_name": "Apex Cloud",
            "source_url": "https://example.com/job/1",
            "salary_raw": "$150,000 - $180,000",
            "posted_date_raw": "2026-10-15",
        }
        val, reasons = SchemaValidator.validate_and_transform_record(row)
        assert reasons == []
        assert val is not None
        assert val["salary_min"] == 150000.0
        assert val["location"] == "Unspecified"  # Imputed
        assert val["employment_type"] == "Full-time"  # Imputed

    def test_missing_mandatory_title_rejected(self):
        row = {
            "job_title": "",  # Missing!
            "company_name": "Apex Cloud",
            "source_url": "https://example.com/job/1",
        }
        val, reasons = SchemaValidator.validate_and_transform_record(row)
        assert val is None
        assert any("Missing mandatory required field: 'job_title'" in r for r in reasons)

    def test_dataset_deduplication(self):
        records = [
            {"job_title": "Data Engineer", "company_name": "Apex", "source_url": "https://example.com/1"},
            {"job_title": "Data Engineer", "company_name": "Apex", "source_url": "https://example.com/1"},  # Dup
        ]
        df = pd.DataFrame(records)
        clean_df, rejections, summary = SchemaValidator.validate_dataset(df, deduplicate=True)
        assert len(clean_df) == 1
        assert summary["duplicates_removed"] == 1
        assert len(rejections) == 1


class TestQualityProfiler:
    """Tests for profile reports."""

    def test_profile_generation(self, tmp_path: Path):
        raw_df = pd.DataFrame({
            "Job Title": ["Engineer", "Architect", None],
            "Salary": ["$100k", None, "$120k"],
        })
        clean_df = pd.DataFrame({
            "job_title": ["Engineer", "Architect"],
            "salary_min": [100000.0, 120000.0],
        })
        rep = QualityProfiler.generate_comparison_report(
            raw_df=raw_df,
            cleaned_df=clean_df,
            rejected_records=[{"row_index": 3, "reasons": ["Missing title"]}],
            validation_summary={"duplicates_removed": 0, "acceptance_rate_pct": 66.67},
            cleaning_metadata={"renamed_columns": {"Job Title": "job_title"}},
        )
        assert rep["overall_status"] == "PASS"
        assert rep["summary"]["input_record_count"] == 3
        assert rep["summary"]["output_clean_record_count"] == 2
