"""SQLAlchemy 2.0 declarative database models, indexes, and schema constraints."""

from __future__ import annotations

import datetime
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Float,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class JobListing(Base):
    """Relational model for cleaned and validated technical job listings."""

    __tablename__ = "job_listings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    fingerprint_hash = Column(String(64), unique=True, nullable=False, index=True)
    job_title = Column(String(255), nullable=False, index=True)
    company_name = Column(String(255), nullable=False, index=True)
    salary_raw = Column(String(255), default="")
    salary_min = Column(Numeric(12, 2), nullable=True)
    salary_max = Column(Numeric(12, 2), nullable=True)
    salary_avg = Column(Numeric(12, 2), nullable=True)
    currency = Column(String(10), default="USD", nullable=True)
    location = Column(String(255), default="Unspecified")
    category = Column(String(100), default="General")
    employment_type = Column(String(50), default="Full-time")
    posted_date = Column(String(20), nullable=True, index=True)
    source_url = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        # Optimized composite index for high-cardinality multi-attribute queries
        Index("idx_jobs_category_location", "category", "location"),
        Index("idx_jobs_currency_salary", "currency", "salary_avg"),
        # Check constraints enforcing domain integrity
        CheckConstraint(
            "salary_min IS NULL OR salary_min >= 0",
            name="ck_job_salary_min_non_negative",
        ),
        CheckConstraint(
            "salary_min IS NULL OR salary_max IS NULL OR salary_max >= salary_min",
            name="ck_job_salary_range_valid",
        ),
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "fingerprint_hash": self.fingerprint_hash,
            "job_title": self.job_title,
            "company_name": self.company_name,
            "salary_raw": self.salary_raw,
            "salary_min": float(self.salary_min) if self.salary_min is not None else None,
            "salary_max": float(self.salary_max) if self.salary_max is not None else None,
            "salary_avg": float(self.salary_avg) if self.salary_avg is not None else None,
            "currency": self.currency,
            "location": self.location,
            "category": self.category,
            "employment_type": self.employment_type,
            "posted_date": self.posted_date,
            "source_url": self.source_url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class PipelineExecution(Base):
    """Persistent audit log of ETL pipeline executions and stage health."""

    __tablename__ = "pipeline_executions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    execution_id = Column(String(64), unique=True, nullable=False, index=True)
    trigger_type = Column(String(50), default="manual", nullable=False)
    is_dry_run = Column(Boolean, default=False, nullable=False)
    status = Column(String(50), default="RUNNING", nullable=False)
    start_time = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=True)
    duration_seconds = Column(Float, default=0.0)
    records_extracted = Column(Integer, default=0)
    records_cleaned = Column(Integer, default=0)
    records_inserted = Column(Integer, default=0)
    records_updated = Column(Integer, default=0)
    records_rejected = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "execution_id": self.execution_id,
            "trigger_type": self.trigger_type,
            "is_dry_run": self.is_dry_run,
            "status": self.status,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": self.duration_seconds,
            "records_extracted": self.records_extracted,
            "records_cleaned": self.records_cleaned,
            "records_inserted": self.records_inserted,
            "records_updated": self.records_updated,
            "records_rejected": self.records_rejected,
            "error_message": self.error_message,
        }
