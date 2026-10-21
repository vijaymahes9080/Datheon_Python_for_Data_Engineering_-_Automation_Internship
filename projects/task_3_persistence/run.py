"""Task 3 Independent Entry Point: Relational Database Auto-Ingestion & Upsert Engine."""

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
from src.persistence.analytics import DatabaseAnalytics
from src.persistence.connection import get_engine, init_database_schema
from src.persistence.repository import JobRepository


def setup_cli_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def load_dataset(input_path: Path) -> list[dict]:
    """Load dataset from CSV or JSON into list of dicts."""
    if not input_path.exists():
        raise FileNotFoundError(f"Cleaned dataset not found: {input_path}")
    if input_path.suffix.lower() == ".csv":
        return pd.read_csv(input_path).to_dict(orient="records")
    return pd.read_json(input_path).to_dict(orient="records")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="StreamForge Task 3: Relational Database Auto-Ingestion & Upsert Engine"
    )
    parser.add_argument(
        "--input",
        type=str,
        default=None,
        help="Path to cleaned CSV or JSON (default: checks data/processed/cleaned_jobs.csv)",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=50,
        help="Batch size for database upserts (default: 50)",
    )
    parser.add_argument(
        "--test-rollback",
        action="store_true",
        help="Run explicit transaction rollback verification test",
    )
    parser.add_argument(
        "--db-url",
        type=str,
        default=None,
        help="Optional database URL override (defaults to settings SQLite or PostgreSQL)",
    )

    args = parser.parse_args()
    setup_cli_logging()

    # Determine input file
    if args.input:
        in_path = Path(args.input)
    else:
        candidate = settings.DATA_PROCESSED_DIR / "cleaned_jobs.csv"
        if not candidate.exists():
            # If Task 2 hasn't run yet, fall back to fixtures
            candidate = settings.DATA_FIXTURES_DIR / "raw_mock_jobs.csv"
        in_path = candidate

    engine = get_engine(db_url=args.db_url)
    repo = JobRepository(engine=engine, batch_size=args.batch_size)
    analytics = DatabaseAnalytics(engine=engine)

    print("\n" + "=" * 70)
    print(" STREAMFORGE — TASK 3: DATABASE INGESTION & UPSERT ENGINE")
    print("=" * 70)
    print(f" Database Target:  {engine.url.render_as_string(hide_password=True)}")
    print(f" Input Dataset:    {in_path}")
    print(f" Batch Size:       {args.batch_size}")
    print("=" * 70 + "\n")

    # 1. Initialize schema
    init_database_schema(engine=engine)
    initial_count = repo.get_total_count()
    print(f"[*] Initial stored database records: {initial_count}")

    # 2. Load dataset and perform first upsert pass
    records = load_dataset(in_path)
    print(f"[*] Ingesting {len(records)} records...")
    pass_1_report = repo.upsert_records(records)

    # 3. Test Idempotence by running repeated upsert
    print("[*] Testing idempotence with second ingestion pass on identical dataset...")
    pass_2_report = repo.upsert_records(records)

    # 4. Rollback Verification Test
    rollback_status = "N/A"
    if args.test_rollback:
        print("[*] Executing transaction rollback safety test (simulated failure)...")
        rollback_success = not repo.execute_transaction_with_rollback_test(
            [{"fingerprint_hash": "TEST_ROLLBACK_FP_123", "job_title": "Rollback Test", "company_name": "Test Co"}],
            simulate_failure=True,
        )
        rollback_status = "PASSED (Safe Rollback Confirmed)" if rollback_success else "FAILED"
        print(f"[*] Rollback Verification: {rollback_status}")

    # 5. Run Verification Analytics
    verification = analytics.generate_verification_report()

    print("\n" + "-" * 70)
    print(" DATABASE INGESTION & IDEMPOTENCE AUDIT SUMMARY")
    print("-" * 70)
    print(f" First Pass Inserted:       {pass_1_report.inserted}")
    print(f" First Pass Updated:        {pass_1_report.updated}")
    print(f" Second Pass Inserted:      {pass_2_report.inserted} (Should be 0 for idempotence)")
    print(f" Second Pass Updated:       {pass_2_report.updated}")
    print(f" Total Stored in DB:        {verification['total_records']}")
    print(f" Duplicate Check (HAVING > 1): {verification['duplicate_count']} duplicates found")
    print(f" Rollback Test Status:      {rollback_status}")
    print(f" Audit Report:              {settings.REPORTS_DIR / 'database_load_report.json'}")
    print("-" * 70)

    # Validate idempotence condition: Second pass inserted MUST be 0!
    if pass_2_report.inserted == 0 and verification["duplicate_audit_passed"]:
        print(" [PASS] Idempotence verified: 0 duplicates created on repeated ingestion.\n")
        return 0
    else:
        print(" [FAIL] Idempotence violation detected: Duplicate records created.\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
