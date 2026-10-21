"""Export routines for extracted raw records into CSV and JSON formats."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any
import pandas as pd

from config.settings import settings

logger = logging.getLogger("streamforge.extraction.exporter")


def export_to_csv(records: list[dict[str, Any]], target_path: Path | None = None) -> Path:
    """Export raw records to CSV format.

    Args:
        records: List of record dictionaries.
        target_path: Optional destination path. Defaults to settings.DATA_RAW_DIR / 'extracted_jobs.csv'.

    Returns:
        Path to the saved CSV file.
    """
    path = target_path or (settings.DATA_RAW_DIR / "extracted_jobs.csv")
    path.parent.mkdir(parents=True, exist_ok=True)

    if not records:
        logger.warning(f"No records to export to CSV at {path}. Writing empty header.")
        df = pd.DataFrame(columns=[
            "fingerprint_hash", "job_title", "company_name", "salary_raw",
            "location", "category", "employment_type", "posted_date_raw",
            "source_url", "extraction_timestamp"
        ])
    else:
        df = pd.DataFrame(records)

    df.to_csv(path, index=False, encoding="utf-8")
    logger.info(f"Exported {len(df)} records to CSV: {path} ({path.stat().st_size} bytes)")
    return path


def export_to_json(records: list[dict[str, Any]], target_path: Path | None = None) -> Path:
    """Export raw records to JSON format with 2-space indentation.

    Args:
        records: List of record dictionaries.
        target_path: Optional destination path. Defaults to settings.DATA_RAW_DIR / 'extracted_jobs.json'.

    Returns:
        Path to the saved JSON file.
    """
    path = target_path or (settings.DATA_RAW_DIR / "extracted_jobs.json")
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)

    logger.info(f"Exported {len(records)} records to JSON: {path} ({path.stat().st_size} bytes)")
    return path


def export_extracted_dataset(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Convenience helper exporting to both CSV and JSON.

    Returns:
        Dictionary containing file paths, record count, and byte sizes.
    """
    csv_file = export_to_csv(records)
    json_file = export_to_json(records)

    return {
        "record_count": len(records),
        "csv_path": str(csv_file),
        "csv_size_bytes": csv_file.stat().st_size,
        "json_path": str(json_file),
        "json_size_bytes": json_file.stat().st_size,
    }
