"""Idempotent upsert engine and repository for JobListing persistence."""

from __future__ import annotations

import logging
from typing import Any
import pandas as pd
from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from src.persistence.connection import get_engine, get_session
from src.persistence.models import JobListing

logger = logging.getLogger("streamforge.persistence.repository")


class IngestionReport:
    """Record of database ingestion outcomes and counters."""

    def __init__(self):
        self.total_input: int = 0
        self.inserted: int = 0
        self.updated: int = 0
        self.unchanged: int = 0
        self.failed: int = 0
        self.errors: list[str] = []

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_input": self.total_input,
            "inserted": self.inserted,
            "updated": self.updated,
            "unchanged": self.unchanged,
            "failed": self.failed,
            "errors": self.errors,
        }


class JobRepository:
    """Dialect-aware repository supporting atomic, idempotent upserting."""

    def __init__(self, engine: Engine | None = None, batch_size: int = 50):
        self.engine = engine or get_engine()
        self.batch_size = batch_size
        self.is_sqlite = self.engine.url.drivername.startswith("sqlite")

    def upsert_records(self, records: list[dict[str, Any]]) -> IngestionReport:
        """Idempotently insert new records or update existing ones on fingerprint conflict.

        Batched and transactional with precise counters.
        """
        report = IngestionReport()
        report.total_input = len(records)

        if not records:
            logger.info("No records provided for upsert.")
            return report

        # Filter and normalize incoming dicts
        valid_records: list[dict[str, Any]] = []
        for r in records:
            clean_r = {
                "fingerprint_hash": r.get("fingerprint_hash"),
                "job_title": r.get("job_title"),
                "company_name": r.get("company_name"),
                "salary_raw": r.get("salary_raw", ""),
                "salary_min": r.get("salary_min"),
                "salary_max": r.get("salary_max"),
                "salary_avg": r.get("salary_avg"),
                "currency": r.get("currency", "USD"),
                "location": r.get("location", "Unspecified"),
                "category": r.get("category", "General"),
                "employment_type": r.get("employment_type", "Full-time"),
                "posted_date": r.get("posted_date"),
                "source_url": r.get("source_url", ""),
            }
            if clean_r["fingerprint_hash"] and clean_r["job_title"]:
                valid_records.append(clean_r)
            else:
                report.failed += 1
                report.errors.append(f"Skipping record with missing required attributes: {r}")

        # Execute in batches
        for i in range(0, len(valid_records), self.batch_size):
            batch = valid_records[i : i + self.batch_size]
            self._upsert_batch(batch, report)

        logger.info(
            f"Upsert complete: {report.inserted} inserted, "
            f"{report.updated} updated, {report.failed} failed."
        )
        return report

    def _upsert_batch(self, batch: list[dict[str, Any]], report: IngestionReport) -> None:
        """Upsert a single batch using native dialect conflict clauses."""
        with get_session(self.engine) as session:
            # Query existing records in this batch to determine inserted vs updated counts
            fps = [r["fingerprint_hash"] for r in batch]
            existing_fps = set(
                session.scalars(
                    select(JobListing.fingerprint_hash).where(JobListing.fingerprint_hash.in_(fps))
                ).all()
            )

            update_cols = {
                "job_title": None,
                "company_name": None,
                "salary_raw": None,
                "salary_min": None,
                "salary_max": None,
                "salary_avg": None,
                "currency": None,
                "location": None,
                "category": None,
                "employment_type": None,
                "posted_date": None,
                "source_url": None,
                "updated_at": func.now(),
            }

            if self.is_sqlite:
                stmt = sqlite_insert(JobListing).values(batch)
                stmt = stmt.on_conflict_do_update(
                    index_elements=[JobListing.fingerprint_hash],
                    set_={
                        col: getattr(stmt.excluded, col)
                        for col in update_cols
                        if col != "updated_at"
                    } | {"updated_at": func.now()},
                )
            else:
                stmt = pg_insert(JobListing).values(batch)
                stmt = stmt.on_conflict_do_update(
                    index_elements=[JobListing.fingerprint_hash],
                    set_={
                        col: getattr(stmt.excluded, col)
                        for col in update_cols
                        if col != "updated_at"
                    } | {"updated_at": func.now()},
                )

            session.execute(stmt)

            # Update report metrics
            for r in batch:
                if r["fingerprint_hash"] in existing_fps:
                    report.updated += 1
                else:
                    report.inserted += 1

    def get_total_count(self) -> int:
        """Return total count of stored job listings."""
        with get_session(self.engine) as session:
            count = session.scalar(select(func.count(JobListing.id)))
            return int(count or 0)
