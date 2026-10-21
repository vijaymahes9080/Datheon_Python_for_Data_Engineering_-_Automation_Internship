"""StreamForge Dashboard: Page 2 - Extraction Studio."""

from __future__ import annotations

import json
from pathlib import Path
import pandas as pd
import streamlit as st

from config.settings import settings
from src.extraction.scraper import StreamForgeScraper

st.set_page_config(page_title="Extraction Studio | StreamForge", page_icon="🌐", layout="wide")

st.title("🌐 Extraction Studio")
st.markdown("Configure web crawling targets, request delays, exponential backoffs, and inspect extracted raw records.")

# Sidebar Controls for Extraction
with st.sidebar:
    st.subheader("⚙️ Scraper Configuration")
    is_offline = st.toggle("Offline Fixture Mode", value=True, help="Use bundled HTML test fixtures without network dependency")
    
    if is_offline:
        default_url = "page_1.html"
        st.info("Using bundled test fixtures in `data/fixtures/html/`")
    else:
        default_url = "https://forge-jobs.internal/listings"

    start_url = st.text_input("Starting URL / Fixture", value=default_url)
    max_pages = st.slider("Max Pages to Traverse", min_value=1, max_value=10, value=3)
    record_limit = st.number_input("Max Records to Extract", min_value=10, max_value=500, value=150, step=10)
    delay_sec = st.slider("Request Pacing Delay (seconds)", min_value=0.0, max_value=5.0, value=0.0 if is_offline else 1.0, step=0.5)

    run_scraper_btn = st.button("🚀 Run Extractor Now", type="primary")

# Execute Scraper if requested
if run_scraper_btn:
    with st.spinner(f"Extracting records from {start_url}..."):
        scraper = StreamForgeScraper(
            base_url=start_url,
            max_pages=max_pages,
            record_limit=record_limit,
            delay_sec=delay_sec,
            is_offline=is_offline,
        )
        records, report = scraper.run()
        st.success(
            f"Extraction completed in {report.elapsed_seconds}s! "
            f"Extracted {report.records_extracted_total} raw records, "
            f"eliminated {report.duplicates_removed} duplicates, "
            f"retained {report.unique_records_retained} unique records."
        )

# Display latest extraction report
report_path = settings.REPORTS_DIR / "extraction_report.json"
csv_path = settings.DATA_RAW_DIR / "extracted_jobs.csv"
json_path = settings.DATA_RAW_DIR / "extracted_jobs.json"

if report_path.exists():
    try:
        report_data = json.loads(report_path.read_text(encoding="utf-8"))
    except Exception:
        report_data = {}

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Pages Visited", report_data.get("pages_visited_count", 0))
    with m2:
        st.metric("Raw Extracted", report_data.get("records_extracted_total", 0))
    with m3:
        st.metric("Duplicates Dropped", report_data.get("duplicates_removed", 0))
    with m4:
        st.metric("Unique Retained", report_data.get("unique_records_retained", 0))

    st.markdown("---")

    # Download Buttons
    d1, d2, d3 = st.columns([1, 1, 4])
    if csv_path.exists():
        with d1:
            st.download_button(
                label="📥 Download Raw CSV",
                data=csv_path.read_bytes(),
                file_name="extracted_jobs.csv",
                mime="text/csv",
            )
    if json_path.exists():
        with d2:
            st.download_button(
                label="📥 Download Raw JSON",
                data=json_path.read_bytes(),
                file_name="extracted_jobs.json",
                mime="application/json",
            )

    # Raw Data Preview Table
    st.subheader("📋 Extracted Records Preview")
    if csv_path.exists():
        df_raw = pd.read_csv(csv_path)
        st.dataframe(df_raw, use_container_width=True, hide_index=True)
        st.caption(f"Showing {len(df_raw)} records loaded from `{csv_path}`")
    else:
        st.info("No raw extracted CSV found. Trigger an extraction run above.")

else:
    st.info("No extraction runs recorded yet. Click 'Run Extractor Now' in the sidebar.")
