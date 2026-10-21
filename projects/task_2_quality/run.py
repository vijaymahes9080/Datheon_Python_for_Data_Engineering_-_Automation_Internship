"""Task 2 Independent Entry Point: Automated Data Cleaning & Schema Transformation."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
import pandas as pd

# Ensure package root is in sys.path
PACKAGE_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from config.settings import settings
from src.quality.cleaner import DataCleaner
from src.quality.profiler import QualityProfiler
from src.quality.validator import SchemaValidator


def setup_cli_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def load_input_data(input_path: Path) -> pd.DataFrame:
    """Load dataset from CSV or JSON format."""
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    if input_path.suffix.lower() == ".csv":
        return pd.read_csv(input_path)
    elif input_path.suffix.lower() == ".json":
        return pd.read_json(input_path)
    else:
        raise ValueError(f"Unsupported file format: {input_path.suffix}. Use .csv or .json")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="StreamForge Task 2: Automated Data Cleaning & Schema Transformation"
    )
    parser.add_argument(
        "--input",
        type=str,
        default=None,
        help="Path to input CSV or JSON (default: checks raw_mock_jobs.csv then extracted_jobs.csv)",
    )
    parser.add_argument(
        "--output-csv",
        type=str,
        default=str(settings.DATA_PROCESSED_DIR / "cleaned_jobs.csv"),
        help="Destination path for cleaned CSV",
    )
    parser.add_argument(
        "--output-json",
        type=str,
        default=str(settings.DATA_PROCESSED_DIR / "cleaned_jobs.json"),
        help="Destination path for cleaned JSON",
    )
    parser.add_argument(
        "--no-dedup",
        action="store_true",
        help="Skip deduplication during validation",
    )

    args = parser.parse_args()
    setup_cli_logging()

    # Determine input path
    if args.input:
        in_path = Path(args.input)
    else:
        # Default priority: raw_mock_jobs.csv (messy test set) -> extracted_jobs.csv
        candidate_1 = settings.DATA_FIXTURES_DIR / "raw_mock_jobs.csv"
        candidate_2 = settings.DATA_RAW_DIR / "extracted_jobs.csv"
        in_path = candidate_1 if candidate_1.exists() else candidate_2

    print("\n" + "=" * 70)
    print(" STREAMFORGE — TASK 2: DATA CLEANING & SCHEMA TRANSFORMATION")
    print("=" * 70)
    print(f" Input Dataset:   {in_path}")
    print(f" Output CSV:      {args.output_csv}")
    print(f" Output JSON:     {args.output_json}")
    print("=" * 70 + "\n")

    # 1. Load Data
    raw_df = load_input_data(in_path)
    print(f"[*] Loaded {len(raw_df)} input records with {len(raw_df.columns)} columns.")

    # 2. Standardize & Clean
    cleaned_df, cleaning_meta = DataCleaner.clean(raw_df)

    # 3. Validate & Segregate
    valid_df, rejected_records, val_summary = SchemaValidator.validate_dataset(
        cleaned_df, deduplicate=(not args.no_dedup)
    )

    # 4. Generate Quality Profiling Reports
    report = QualityProfiler.generate_comparison_report(
        raw_df=raw_df,
        cleaned_df=valid_df,
        rejected_records=rejected_records,
        validation_summary=val_summary,
        cleaning_metadata=cleaning_meta,
    )

    # 5. Save Outputs
    out_csv = Path(args.output_csv)
    out_json = Path(args.output_json)
    out_csv.parent.mkdir(parents=True, exist_ok=True)

    valid_df.to_csv(out_csv, index=False, encoding="utf-8")
    valid_df.to_json(out_json, orient="records", indent=2)

    print("\n" + "-" * 70)
    print(" DATA QUALITY & VALIDATION SUMMARY")
    print("-" * 70)
    print(f" Input Records:           {val_summary['total_input_records']}")
    print(f" Valid Accepted Records:  {val_summary['accepted_count']}")
    print(f" Rejected Records:        {val_summary['rejected_count']}")
    print(f" Duplicates Removed:      {val_summary['duplicates_removed']}")
    print(f" Acceptance Rate:         {val_summary['acceptance_rate_pct']}%")
    print(f" Validation Report:       {settings.REPORTS_DIR / 'validation_report.json'}")
    print(f" Rejection Ledger:        {settings.REPORTS_DIR / 'rejected_records.json'}")
    print(f" Markdown Summary:        {settings.REPORTS_DIR / 'validation_summary.md'}")
    print("-" * 70)

    if val_summary["accepted_count"] > 0:
        print(" [PASS] Task 2 completed successfully with validated outputs.\n")
        return 0
    else:
        print(" [FAIL] No records passed validation.\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
