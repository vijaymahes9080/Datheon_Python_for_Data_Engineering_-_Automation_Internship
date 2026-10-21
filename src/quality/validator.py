"""Schema validation and row rejection engine."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any
import pandas as pd
from pydantic import ValidationError

from config.schema_rules import (
    ALLOWED_EMPLOYMENT_TYPES,
    DEFAULT_IMPUTATIONS,
    JobListingSchema,
    REQUIRED_FIELDS,
)
from config.settings import settings
from src.extraction.fingerprint import generate_record_fingerprint
from src.quality.parsers import parse_and_normalize_date, parse_salary_and_currency

logger = logging.getLogger("streamforge.quality.validator")


class SchemaValidator:
    """Validates cleaned records, applies missing-value policies, and isolates rejected rows."""

    @classmethod
    def validate_and_transform_record(cls, row: dict[str, Any]) -> tuple[dict[str, Any] | None, list[str]]:
        """Validate an individual record dictionary.

        Returns:
            (validated_record_dict, rejection_reasons_list)
        """
        reasons: list[str] = []

        # 1. Check Required Fields
        for req in REQUIRED_FIELDS:
            val = row.get(req)
            if val is None or str(val).strip() == "" or pd.isna(val):
                reasons.append(f"Missing mandatory required field: '{req}'")

        # 2. Impute missing non-mandatory fields
        imputed = dict(row)
        for field, default_val in DEFAULT_IMPUTATIONS.items():
            if imputed.get(field) is None or str(imputed.get(field)).strip() == "" or pd.isna(imputed.get(field)):
                imputed[field] = default_val

        # 3. Standardize employment type
        emp_key = str(imputed.get("employment_type", "")).strip().lower()
        imputed["employment_type"] = ALLOWED_EMPLOYMENT_TYPES.get(emp_key, "Full-time")

        # 4. Parse & Validate Salary / Compensation
        sal_meta = parse_salary_and_currency(imputed.get("salary_raw"))
        imputed["salary_min"] = sal_meta["salary_min"]
        imputed["salary_max"] = sal_meta["salary_max"]
        imputed["salary_avg"] = sal_meta["salary_avg"]
        imputed["currency"] = sal_meta["currency"] or "USD"

        # Check salary logical invariants
        if (
            imputed["salary_min"] is not None
            and imputed["salary_max"] is not None
            and imputed["salary_min"] > imputed["salary_max"]
        ):
            reasons.append(f"Invalid salary range: min ({imputed['salary_min']}) > max ({imputed['salary_max']})")

        # 5. Parse & Normalize Date
        date_iso, is_valid_date, date_reason = parse_and_normalize_date(imputed.get("posted_date_raw"))
        if is_valid_date:
            imputed["posted_date"] = date_iso
        else:
            # If date is invalid or in future, flag it
            reasons.append(f"Date validation failure: {date_reason}")

        # 6. If any validation checks failed, reject early before fingerprinting
        if reasons:
            return None, reasons

        # 7. Ensure Fingerprint Hash exists
        if not imputed.get("fingerprint_hash"):
            imputed["fingerprint_hash"] = generate_record_fingerprint(imputed)

        # 7. Final Pydantic Schema Model Validation
        try:
            schema_instance = JobListingSchema(**imputed)
            return schema_instance.model_dump(), []
        except ValidationError as exc:
            for err in exc.errors():
                loc = " -> ".join(str(l) for l in err["loc"])
                reasons.append(f"Schema violation at '{loc}': {err['msg']}")
            return None, reasons

    @classmethod
    def validate_dataset(
        cls, df: pd.DataFrame, deduplicate: bool = True
    ) -> tuple[pd.DataFrame, list[dict[str, Any]], dict[str, Any]]:
        """Validate entire DataFrame, separating accepted and rejected records."""
        accepted_records: list[dict[str, Any]] = []
        rejected_records: list[dict[str, Any]] = []
        seen_fingerprints: set[str] = set()
        duplicates_removed = 0

        records = df.to_dict(orient="records")

        for idx, row in enumerate(records):
            validated, reasons = cls.validate_and_transform_record(row)

            if reasons:
                rejected_records.append({
                    "row_index": idx + 1,
                    "record": row,
                    "reasons": reasons,
                })
            else:
                fp = validated["fingerprint_hash"]
                if deduplicate and fp in seen_fingerprints:
                    duplicates_removed += 1
                    rejected_records.append({
                        "row_index": idx + 1,
                        "record": row,
                        "reasons": [f"Duplicate record detected with fingerprint {fp}"],
                    })
                else:
                    seen_fingerprints.add(fp)
                    accepted_records.append(validated)

        accepted_df = pd.DataFrame(accepted_records) if accepted_records else pd.DataFrame()

        summary = {
            "total_input_records": len(df),
            "accepted_count": len(accepted_records),
            "rejected_count": len(rejected_records),
            "duplicates_removed": duplicates_removed,
            "acceptance_rate_pct": round((len(accepted_records) / len(df) * 100) if len(df) > 0 else 0, 2),
        }

        # Save rejected records report
        rejections_path = settings.REPORTS_DIR / "rejected_records.json"
        rejections_path.parent.mkdir(parents=True, exist_ok=True)
        with open(rejections_path, "w", encoding="utf-8") as f:
            json.dump(rejected_records, f, indent=2, default=str)

        logger.info(
            f"Validation complete: {len(accepted_records)} accepted, "
            f"{len(rejected_records)} rejected ({duplicates_removed} duplicates)"
        )

        return accepted_df, rejected_records, summary
