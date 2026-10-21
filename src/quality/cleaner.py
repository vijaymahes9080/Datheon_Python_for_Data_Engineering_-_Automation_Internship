"""Data cleaning module: column standardization and whitespace normalization."""

from __future__ import annotations

import logging
import re
from typing import Any
import numpy as np
import pandas as pd

logger = logging.getLogger("streamforge.quality.cleaner")

# Canonical column mapping dictionary
COLUMN_ALIAS_MAP: dict[str, str] = {
    "record_id": "record_id",
    "id": "record_id",
    "job_title": "job_title",
    "title": "job_title",
    "position": "job_title",
    "role": "job_title",
    "company_name": "company_name",
    "company": "company_name",
    "organization": "company_name",
    "employer": "company_name",
    "salary_raw": "salary_raw",
    "salary": "salary_raw",
    "compensation": "salary_raw",
    "salary_compensation": "salary_raw",
    "location": "location",
    "location_city_country": "location",
    "city": "location",
    "category": "category",
    "job_category": "category",
    "department": "category",
    "employment_type": "employment_type",
    "job_type": "employment_type",
    "type": "employment_type",
    "posted_date_raw": "posted_date_raw",
    "posted_date": "posted_date_raw",
    "date_posted": "posted_date_raw",
    "date": "posted_date_raw",
    "source_url": "source_url",
    "url": "source_url",
    "link": "source_url",
    "fingerprint_hash": "fingerprint_hash",
    "hash": "fingerprint_hash",
}


def to_snake_case(text: str) -> str:
    """Convert arbitrary header text into clean snake_case."""
    # Remove parentheses, brackets, special punctuation
    cleaned = re.sub(r"[\(\)\[\]\{\}\/\\,;:\.\?\!@#\$%\^&\*~`\"']", " ", str(text))
    # Replace whitespace and hyphens with single underscore
    cleaned = re.sub(r"[\s\-]+", "_", cleaned.strip())
    # Convert PascalCase/camelCase to snake_case
    cleaned = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", cleaned)
    # Deduplicate underscores and lowercase
    cleaned = re.sub(r"_+", "_", cleaned).strip("_").lower()
    return cleaned


class DataCleaner:
    """Standardizes tabular headers and normalizes string fields."""

    @staticmethod
    def standardize_headers(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, str]]:
        """Rename all DataFrame columns to snake_case and align with canonical aliases."""
        rename_map: dict[str, str] = {}
        for col in df.columns:
            snake = to_snake_case(str(col))
            canonical = COLUMN_ALIAS_MAP.get(snake, snake)
            rename_map[col] = canonical

        renamed_df = df.rename(columns=rename_map)
        logger.info(f"Standardized {len(rename_map)} columns into canonical snake_case")
        return renamed_df, rename_map

    @staticmethod
    def normalize_text_fields(df: pd.DataFrame) -> pd.DataFrame:
        """Strip extra whitespace, normalize spaces, and replace blank strings with np.nan."""
        cleaned_df = df.copy()

        for col in cleaned_df.select_dtypes(include=["object", "string"]).columns:
            # Replace whitespace-only strings with NaN
            cleaned_df[col] = cleaned_df[col].apply(
                lambda val: None if (pd.isna(val) or str(val).strip() == "") else re.sub(r"\s+", " ", str(val).strip())
            )

        return cleaned_df

    @classmethod
    def clean(cls, df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
        """Perform full baseline cleaning: header normalization and text trimming."""
        renamed_df, rename_map = cls.standardize_headers(df)
        normalized_df = cls.normalize_text_fields(renamed_df)

        metadata = {
            "initial_rows": len(df),
            "initial_columns": list(df.columns),
            "renamed_columns": rename_map,
            "final_columns": list(normalized_df.columns),
        }
        return normalized_df, metadata
