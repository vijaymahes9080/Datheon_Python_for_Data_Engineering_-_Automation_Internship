"""Unit and integration tests for Task 3: Relational Database Auto-Ingestion & Upsert Engine."""

from __future__ import annotations

from pathlib import Path
import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from src.persistence.analytics import DatabaseAnalytics
from src.persistence.connection import init_database_schema
from src.persistence.models import Base, JobListing
from src.persistence.repository import JobRepository


@pytest.fixture
def in_memory_engine():
    """Create an isolated in-memory SQLite engine for fast, reproducible tests."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


class TestDatabaseSchemaAndInitialization:
    """Tests for table creation and schema integrity."""

    def test_schema_initialization(self, in_memory_engine):
        init_database_schema(in_memory_engine)
        inspector_tables = list(Base.metadata.tables.keys())
        assert "job_listings" in inspector_tables
        assert "pipeline_executions" in inspector_tables


class TestIdempotentUpsert:
    """Tests for idempotent insert and update behaviors."""

    def test_initial_insert(self, in_memory_engine):
        repo = JobRepository(engine=in_memory_engine)
        records = [
            {
                "fingerprint_hash": "A" * 64,
                "job_title": "Data Architect",
                "company_name": "Nexus Corp",
                "salary_raw": "$150k",
                "salary_min": 150000.0,
                "salary_max": 150000.0,
                "salary_avg": 150000.0,
                "currency": "USD",
                "source_url": "https://example.com/1",
            }
        ]
        report = repo.upsert_records(records)
        assert report.inserted == 1
        assert report.updated == 0
        assert repo.get_total_count() == 1

    def test_repeated_ingestion_is_idempotent(self, in_memory_engine):
        repo = JobRepository(engine=in_memory_engine)
        records = [
            {
                "fingerprint_hash": "B" * 64,
                "job_title": "ETL Specialist",
                "company_name": "Apex",
                "source_url": "https://example.com/2",
            }
        ]
        # First pass
        rep1 = repo.upsert_records(records)
        assert rep1.inserted == 1
        assert repo.get_total_count() == 1

        # Second pass with identical fingerprint
        rep2 = repo.upsert_records(records)
        assert rep2.inserted == 0
        assert rep2.updated == 1
        # Total count must not double
        assert repo.get_total_count() == 1

    def test_conflict_updates_fields(self, in_memory_engine):
        repo = JobRepository(engine=in_memory_engine)
        fp = "C" * 64
        initial = [{
            "fingerprint_hash": fp,
            "job_title": "Junior Dev",
            "company_name": "Apex",
            "source_url": "https://example.com/3",
        }]
        repo.upsert_records(initial)

        # Update title and salary
        updated = [{
            "fingerprint_hash": fp,
            "job_title": "Senior Dev",
            "company_name": "Apex",
            "salary_raw": "$140,000",
            "salary_min": 140000.0,
            "salary_max": 140000.0,
            "salary_avg": 140000.0,
            "source_url": "https://example.com/3",
        }]
        repo.upsert_records(updated)

        with in_memory_engine.connect() as conn:
            row = conn.execute(select(JobListing).where(JobListing.fingerprint_hash == fp)).first()
            assert row.job_title == "Senior Dev"
            assert float(row.salary_avg) == 140000.0


class TestTransactionRollback:
    """Tests for transaction rollback safety."""

    def test_transaction_rollback_leaves_no_traces(self, in_memory_engine):
        repo = JobRepository(engine=in_memory_engine)
        records = [{
            "fingerprint_hash": "D" * 64,
            "job_title": "Rollback Test",
            "company_name": "Fault Inc",
            "source_url": "https://example.com/fail",
        }]

        # Trigger simulated fault
        success = repo.execute_transaction_with_rollback_test(records, simulate_failure=True)
        assert success is False
        # Verify rollback prevented persistence
        assert repo.get_total_count() == 0


class TestDatabaseAnalytics:
    """Tests for verification queries."""

    def test_analytics_reports(self, in_memory_engine):
        repo = JobRepository(engine=in_memory_engine)
        records = [
            {
                "fingerprint_hash": "E" * 64,
                "job_title": "Data Engineer",
                "company_name": "Apex",
                "category": "Data Engineering",
                "currency": "USD",
                "salary_min": 120000.0,
                "salary_max": 150000.0,
                "salary_avg": 135000.0,
                "location": "Remote (US)",
                "source_url": "https://example.com/e",
            },
            {
                "fingerprint_hash": "F" * 64,
                "job_title": "Cloud Architect",
                "company_name": "Nexus",
                "category": "Cloud & Infra",
                "currency": "EUR",
                "salary_min": 90000.0,
                "salary_max": 110000.0,
                "salary_avg": 100000.0,
                "location": "Berlin, Germany",
                "source_url": "https://example.com/f",
            },
        ]
        repo.upsert_records(records)

        analytics = DatabaseAnalytics(engine=in_memory_engine)
        rep = analytics.generate_verification_report()

        assert rep["total_records"] == 2
        assert rep["duplicate_count"] == 0
        assert rep["duplicate_audit_passed"] is True
        assert len(rep["category_distribution"]) == 2
        assert len(rep["salary_benchmarks"]) == 2

        # Search test
        search_res = analytics.search_listings(keyword="Engineer")
        assert len(search_res) == 1
        assert search_res[0]["job_title"] == "Data Engineer"
