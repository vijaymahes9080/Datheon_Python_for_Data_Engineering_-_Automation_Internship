"""Analytical verification queries, database audit metrics, and report generator."""

from __future__ import annotations

import datetime
import json
import logging
from pathlib import Path
from typing import Any
import pandas as pd
from sqlalchemy import desc, func, select
from sqlalchemy.engine import Engine

from config.settings import settings
from src.persistence.connection import get_engine, get_session
from src.persistence.models import JobListing

logger = logging.getLogger("streamforge.persistence.analytics")


class DatabaseAnalytics:
    """Analytical queries and audit validations for stored job records."""

    def __init__(self, engine: Engine | None = None):
        self.engine = engine or get_engine()

    def check_duplicate_fingerprints(self) -> list[dict[str, Any]]:
        """Verify that zero duplicate fingerprint hashes exist in the table."""
        with get_session(self.engine) as session:
            stmt = (
                select(JobListing.fingerprint_hash, func.count(JobListing.id).label("cnt"))
                .group_by(JobListing.fingerprint_hash)
                .having(func.count(JobListing.id) > 1)
            )
            dups = session.execute(stmt).all()
            return [{"fingerprint_hash": row[0], "count": row[1]} for row in dups]

    def get_category_distribution(self) -> list[dict[str, Any]]:
        """Count of listings grouped by category."""
        with get_session(self.engine) as session:
            stmt = (
                select(JobListing.category, func.count(JobListing.id).label("total_jobs"))
                .group_by(JobListing.category)
                .order_by(desc("total_jobs"))
            )
            rows = session.execute(stmt).all()
            return [{"category": r[0], "total_jobs": r[1]} for r in rows]

    def get_salary_benchmarks(self) -> list[dict[str, Any]]:
        """Compute minimum, maximum, and average salary grouped by currency."""
        with get_session(self.engine) as session:
            stmt = (
                select(
                    JobListing.currency,
                    func.count(JobListing.id).label("listing_count"),
                    func.min(JobListing.salary_min).label("lowest_min"),
                    func.max(JobListing.salary_max).label("highest_max"),
                    func.avg(JobListing.salary_avg).label("overall_average"),
                )
                .where(JobListing.salary_avg.isnot(None))
                .group_by(JobListing.currency)
                .order_by(desc("listing_count"))
            )
            rows = session.execute(stmt).all()
            return [
                {
                    "currency": r[0],
                    "listing_count": r[1],
                    "lowest_min": float(r[2]) if r[2] is not None else None,
                    "highest_max": float(r[3]) if r[3] is not None else None,
                    "overall_average": round(float(r[4]), 2) if r[4] is not None else None,
                }
                for r in rows
            ]

    def get_top_locations(self, limit: int = 10) -> list[dict[str, Any]]:
        """Top hiring locations by volume."""
        with get_session(self.engine) as session:
            stmt = (
                select(JobListing.location, func.count(JobListing.id).label("total"))
                .group_by(JobListing.location)
                .order_by(desc("total"))
                .limit(limit)
            )
            rows = session.execute(stmt).all()
            return [{"location": r[0], "count": r[1]} for r in rows]

    def search_listings(
        self,
        keyword: str | None = None,
        category: str | None = None,
        location: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """Parameterized search query supporting filters across title, company, category, and location."""
        with get_session(self.engine) as session:
            stmt = select(JobListing)

            if keyword:
                kw = f"%{keyword.strip()}%"
                stmt = stmt.where(
                    JobListing.job_title.ilike(kw) | JobListing.company_name.ilike(kw)
                )

            if category and category != "All":
                stmt = stmt.where(JobListing.category == category)

            if location and location != "All":
                stmt = stmt.where(JobListing.location.ilike(f"%{location}%"))

            stmt = stmt.order_by(desc(JobListing.id)).limit(limit).offset(offset)
            results = session.scalars(stmt).all()
            return [r.to_dict() for r in results]

    def generate_verification_report(self) -> dict[str, Any]:
        """Run all audit queries and generate persistent verification report."""
        with get_session(self.engine) as session:
            total_records = int(session.scalar(select(func.count(JobListing.id))) or 0)

        dups = self.check_duplicate_fingerprints()
        categories = self.get_category_distribution()
        salaries = self.get_salary_benchmarks()
        locations = self.get_top_locations()

        report = {
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "database_url": self.engine.url.render_as_string(hide_password=True),
            "total_records": total_records,
            "duplicate_count": len(dups),
            "duplicate_audit_passed": len(dups) == 0,
            "category_distribution": categories,
            "salary_benchmarks": salaries,
            "top_locations": locations,
        }

        # Save to reports/database_load_report.json
        out_file = settings.REPORTS_DIR / "database_load_report.json"
        out_file.parent.mkdir(parents=True, exist_ok=True)
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, default=str)

        logger.info(f"Database verification report saved to {out_file}")
        return report
