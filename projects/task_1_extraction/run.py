"""Task 1 Independent Entry Point: Autonomous Web Scraper & Data Extractor."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

# Ensure package root is in sys.path
PACKAGE_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from config.settings import settings
from src.extraction.scraper import StreamForgeScraper


def setup_cli_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="StreamForge Task 1: Autonomous Web Scraper & Data Extractor"
    )
    parser.add_argument(
        "--url",
        type=str,
        default="page_1.html",
        help="Starting URL or fixture name (default: page_1.html)",
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        default=True,
        help="Run in offline mode using bundled HTML fixtures (default: True)",
    )
    parser.add_argument(
        "--live",
        action="store_false",
        dest="offline",
        help="Run in live HTTP mode connecting to external web target",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=settings.SCRAPER_MAX_PAGES,
        help=f"Maximum pages to traverse (default: {settings.SCRAPER_MAX_PAGES})",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=settings.SCRAPER_MAX_RECORDS,
        help=f"Maximum unique records to extract (default: {settings.SCRAPER_MAX_RECORDS})",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=None,
        help="Pacing delay between requests in seconds",
    )

    args = parser.parse_args()
    setup_cli_logging()

    print("\n" + "=" * 70)
    print(" STREAMFORGE — TASK 1: AUTONOMOUS WEB SCRAPER & DATA EXTRACTOR")
    print("=" * 70)
    print(f" Mode:           {'OFFLINE (Bundled HTML Fixtures)' if args.offline else 'LIVE NETWORK'}")
    print(f" Starting Target: {args.url}")
    print(f" Page Limit:      {args.max_pages}")
    print(f" Record Limit:    {args.limit}")
    print("=" * 70 + "\n")

    scraper = StreamForgeScraper(
        base_url=args.url,
        max_pages=args.max_pages,
        record_limit=args.limit,
        delay_sec=args.delay,
        is_offline=args.offline,
    )

    records, report = scraper.run()

    print("\n" + "-" * 70)
    print(" EXTRACTION RESULTS SUMMARY")
    print("-" * 70)
    print(f" Pages Visited:           {len(report.pages_visited)}")
    print(f" Successful Requests:     {report.successful_requests}")
    print(f" Failed Pages:            {len(report.failed_pages)}")
    print(f" Total Raw Extracted:     {report.records_extracted_total}")
    print(f" Duplicates Filtered:     {report.duplicates_removed}")
    print(f" Unique Records Retained: {report.unique_records_retained}")
    print(f" Elapsed Time:            {report.elapsed_seconds:.3f} seconds")
    print(f" CSV Output:              {report.export_metadata.get('csv_path')}")
    print(f" JSON Output:             {report.export_metadata.get('json_path')}")
    print(f" Audit Report:            {settings.REPORTS_DIR / 'extraction_report.json'}")
    print("-" * 70)

    if report.unique_records_retained >= 100:
        print(f" [PASS] Successfully verified 100+ unique records criteria ({report.unique_records_retained} records).\n")
        return 0
    elif report.unique_records_retained > 0:
        print(f" [INFO] Extracted {report.unique_records_retained} records.\n")
        return 0
    else:
        print(" [FAIL] No records were extracted.\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
