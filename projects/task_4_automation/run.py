"""Task 4 Independent Entry Point: Scheduled End-to-End ETL Pipeline with Alerting."""

from __future__ import annotations

import argparse
import logging
import sys
import time
from pathlib import Path

# Ensure package root is in sys.path
PACKAGE_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from config.logger_config import configure_logging
from config.settings import settings
from src.orchestration.lock import PipelineLock, PipelineLockedException
from src.orchestration.pipeline import ETLPipeline
from src.scheduling.runner import PipelineScheduler


def main() -> int:
    parser = argparse.ArgumentParser(
        description="StreamForge Task 4: Scheduled End-to-End ETL Pipeline with Alerting"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run pipeline in dry-run mode (extract, clean, validate, but skip DB commits)",
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        default=True,
        help="Run using bundled offline fixtures (default: True)",
    )
    parser.add_argument(
        "--live",
        action="store_false",
        dest="offline",
        help="Run in live network extraction mode",
    )
    parser.add_argument(
        "--schedule",
        type=int,
        default=None,
        help="Run in recurring scheduled mode with specified interval in minutes",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=settings.SCRAPER_MAX_PAGES,
        help="Max pages to scrape",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=settings.SCRAPER_MAX_RECORDS,
        help="Max records to extract",
    )

    args = parser.parse_args()
    configure_logging()

    print("\n" + "=" * 75)
    print(" STREAMFORGE — TASK 4: END-TO-END ETL PIPELINE WITH ALERTING")
    print("=" * 75)
    print(f" Execution Mode:   {'DRY RUN (No DB Writes)' if args.dry_run else 'LIVE ETL'}")
    print(f" Extraction Target: {'OFFLINE (Bundled HTML)' if args.offline else 'LIVE NETWORK'}")
    print(f" Recurring Run:    {f'Every {args.schedule} minutes' if args.schedule else 'Single Immediate Execution'}")
    print("=" * 75 + "\n")

    # If scheduled mode is requested
    if args.schedule:
        print(f"[*] Starting recurring scheduler every {args.schedule} minutes. Press Ctrl+C to stop.\n")
        scheduler = PipelineScheduler(
            interval_minutes=args.schedule,
            is_offline=args.offline,
            is_dry_run=args.dry_run,
        )
        scheduler.start(run_immediately=True)
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n[*] Gracefully stopping scheduler...")
            scheduler.stop()
            print("[*] Scheduler stopped.")
            return 0

    # Single execution with concurrency lock
    try:
        with PipelineLock(timeout_seconds=0):
            pipeline = ETLPipeline(
                is_offline=args.offline,
                is_dry_run=args.dry_run,
                trigger_type="cli",
                max_pages=args.max_pages,
                record_limit=args.limit,
            )
            ctx = pipeline.run()

    except PipelineLockedException as exc:
        print(f"\n[FAIL] Concurrency lock error: {exc}")
        return 1

    # Print formatted stage breakdown
    print("\n" + "-" * 75)
    print(" STAGE-BY-STAGE EXECUTION BREAKDOWN")
    print("-" * 75)
    for name, st in ctx.stages.items():
        dur_str = f"{st.duration_seconds:.3f}s" if st.duration_seconds > 0 else "0.000s"
        status_badge = f"[{st.status}]".ljust(11)
        print(f" {status_badge} Stage: {name.ljust(12)} Duration: {dur_str.ljust(8)} Metrics: {st.metrics}")

    print("-" * 75)
    print(f" Total Duration:          {ctx.duration_seconds:.3f} seconds")
    print(f" Final Pipeline Status:   {ctx.status}")
    print(f" Extracted Records:       {len(ctx.raw_records)}")
    print(f" Cleaned Valid Records:   {len(ctx.cleaned_records)}")
    print(f" Database Inserted:       {ctx.ingestion_metrics.get('inserted', 0)}")
    print(f" Database Updated:        {ctx.ingestion_metrics.get('updated', 0)}")
    print(f" Execution Audit Log:     {settings.REPORTS_DIR / 'execution_history.json'}")
    print(f" Rotating Operational Log: {settings.LOGS_DIR / 'streamforge.log'}")
    print("-" * 75)

    if ctx.status == "SUCCESS":
        print(f" [PASS] Full ETL pipeline completed successfully in {ctx.duration_seconds:.3f}s.\n")
        return 0
    else:
        print(f" [FAIL] Pipeline completed with status: {ctx.status}. Error: {ctx.error_message}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
