"""Schema rules and validation constraints configuration."""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field


class JobListingSchema(BaseModel):
    """Pydantic model validating cleaned and transformed job records."""

    fingerprint_hash: str = Field(min_length=64, max_length=64)
    job_title: str = Field(min_length=2, max_length=200)
    company_name: str = Field(min_length=1, max_length=200)
    salary_raw: str = Field(default="")
    salary_min: float | None = Field(default=None, ge=0.0)
    salary_max: float | None = Field(default=None, ge=0.0)
    salary_avg: float | None = Field(default=None, ge=0.0)
    currency: str | None = Field(default="USD", max_length=10)
    location: str = Field(default="Unspecified", max_length=150)
    category: str = Field(default="General", max_length=100)
    employment_type: str = Field(default="Full-time", max_length=50)
    posted_date: str | None = Field(default=None, max_length=20)
    source_url: str = Field(min_length=5, max_length=500)
    extraction_timestamp: str | None = Field(default=None)


# Field constraint rules
REQUIRED_FIELDS = ["job_title", "company_name", "source_url"]

ALLOWED_EMPLOYMENT_TYPES = {
    "full-time": "Full-time",
    "part-time": "Part-time",
    "contract": "Contract",
    "internship": "Internship",
}

DEFAULT_IMPUTATIONS = {
    "location": "Unspecified",
    "category": "General",
    "employment_type": "Full-time",
    "currency": "USD",
}
