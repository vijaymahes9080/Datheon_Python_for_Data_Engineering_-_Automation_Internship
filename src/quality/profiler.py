"""Data quality profiling and before-and-after comparison report generator."""

from __future__ import annotations

import datetime
import json
import logging
from pathlib import Path
from typing import Any
import pandas as pd

from config.settings import settings

logger = logging.getLogger("streamforge.quality.profiler")


class QualityProfiler:
    """Profiles tabular data quality and generates comparative reports."""

    @staticmethod
    def profile_dataframe(df: pd.DataFrame) -> dict[str, Any]:
        """Compute column-level completeness, null counts, and data types."""
        if df.empty:
            return {"record_count": 0, "columns": {}}

        total = len(df)
        cols_profile = {}
        for col in df.columns:
            null_count = int(df[col].isna().sum())
            null_pct = round((null_count / total * 100), 2)
            cols_profile[col] = {
                "dtype": str(df[col].dtype),
                "null_count": null_count,
                "null_percentage": null_pct,
                "unique_values": int(df[col].nunique(dropna=True)),
            }

        return {
            "record_count": total,
            "column_count": len(df.columns),
            "columns": cols_profile,
        }

    @classmethod
    def generate_comparison_report(
        cls,
        raw_df: pd.DataFrame,
        cleaned_df: pd.DataFrame,
        rejected_records: list[dict[str, Any]],
        validation_summary: dict[str, Any],
        cleaning_metadata: dict[str, Any],
    ) -> dict[str, Any]:
        """Generate comprehensive before-and-after quality comparison report."""
        raw_profile = cls.profile_dataframe(raw_df)
        cleaned_profile = cls.profile_dataframe(cleaned_df)

        # Categorize rejection reasons
        reason_counts: dict[str, int] = {}
        for item in rejected_records:
            for r in item.get("reasons", []):
                category = r.split(":")[0] if ":" in r else r
                reason_counts[category] = reason_counts.get(category, 0) + 1

        overall_status = "PASS" if len(cleaned_df) > 0 and len(rejected_records) < len(raw_df) else "FAIL"

        report = {
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "overall_status": overall_status,
            "summary": {
                "input_record_count": len(raw_df),
                "output_clean_record_count": len(cleaned_df),
                "rejected_record_count": len(rejected_records),
                "duplicates_removed": validation_summary.get("duplicates_removed", 0),
                "acceptance_rate_pct": validation_summary.get("acceptance_rate_pct", 0.0),
            },
            "transformations_applied": {
                "columns_renamed": cleaning_metadata.get("renamed_columns", {}),
                "whitespace_trimmed": True,
                "currency_parsed": True,
                "dates_normalized_to_iso": True,
                "missing_values_imputed": ["location", "category", "employment_type"],
            },
            "rejection_reasons_breakdown": reason_counts,
            "before_profile": raw_profile,
            "after_profile": cleaned_profile,
        }

        # Save JSON report
        json_path = settings.REPORTS_DIR / "validation_report.json"
        json_path.parent.mkdir(parents=True, exist_ok=True)
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, default=str)

        # Generate and save Markdown summary
        md_path = settings.REPORTS_DIR / "validation_summary.md"
        cls._save_markdown_summary(report, md_path)

        logger.info(f"Quality profiling reports saved to {json_path} and {md_path}")
        return report

    @staticmethod
    def _save_markdown_summary(report: dict[str, Any], target_path: Path) -> None:
        """Render human-readable Markdown validation summary."""
        s = report["summary"]
        reasons_table = "\n".join(
            f"| {reason} | {count} |" for reason, count in report["rejection_reasons_breakdown"].items()
        ) or "| None | 0 |"

        md_content = f"""# StreamForge Data Quality & Validation Summary

**Execution Timestamp:** `{report['timestamp']}`  
**Overall Validation Status:** **{report['overall_status']}**

---

## 1. Quality Metrics Overview

| Metric | Value |
|:---|:---|
| **Total Input Records** | `{s['input_record_count']}` |
| **Accepted Clean Records** | `{s['output_clean_record_count']}` |
| **Rejected Records** | `{s['rejected_record_count']}` |
| **Duplicates Eliminated** | `{s['duplicates_removed']}` |
| **Data Acceptance Rate** | `{s['acceptance_rate_pct']}%` |

---

## 2. Rejection Reasons Breakdown

| Violation / Cause | Frequency |
|:---|:---|
{reasons_table}

---

## 3. Data Transformations Applied
- **Snake_case Standardization**: Mapped inconsistent column names to canonical schema.
- **Whitespace Normalization**: Removed leading/trailing spaces and collapsed duplicate internal spaces.
- **Currency & Salary Parsing**: Extracted currency codes without silent cross-currency conversion; parsed min/max/avg numbers.
- **Date Normalization**: Standardized diverse formats (`DD/MM/YYYY`, relative days) to ISO-8601 (`YYYY-MM-DD`).
- **Defensive Rejection**: Flagged future dates and missing required fields into `rejected_records.json`.
"""
        target_path.write_text(md_content, encoding="utf-8")
