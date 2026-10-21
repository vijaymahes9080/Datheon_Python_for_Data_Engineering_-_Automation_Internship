"""StreamForge Dashboard: Page 6 - Reports and Logs."""

from __future__ import annotations

import json
from pathlib import Path
import pandas as pd
import streamlit as st

from config.settings import settings

st.set_page_config(page_title="Reports & Logs | StreamForge", page_icon="📜", layout="wide")

st.title("📜 Reports, Audit History & Operational Logs")
st.markdown("Inspect machine-readable artifacts, download generated reports, and search through rotating application logs.")

tab1, tab2, tab3 = st.tabs(["📋 Execution History", "📄 Downloadable Artifacts", "📝 Live Log Viewer"])

# Tab 1: Execution History
with tab1:
    st.subheader("Historical Execution Ledger")
    history_file = settings.REPORTS_DIR / "execution_history.json"
    if history_file.exists():
        try:
            history = json.loads(history_file.read_text(encoding="utf-8"))
        except Exception:
            history = []

        if history:
            rows = []
            for item in history:
                rows.append({
                    "Execution ID": item.get("execution_id"),
                    "Trigger": item.get("trigger_type"),
                    "Mode": "Dry Run" if item.get("is_dry_run") else "Live",
                    "Status": item.get("status"),
                    "Duration (s)": item.get("duration_seconds"),
                    "Extracted": item.get("record_counts", {}).get("extracted", 0),
                    "Cleaned": item.get("record_counts", {}).get("cleaned", 0),
                    "Inserted": item.get("record_counts", {}).get("inserted", 0),
                    "Updated": item.get("record_counts", {}).get("updated", 0),
                    "Rejected": item.get("record_counts", {}).get("rejected", 0),
                    "Start Time": item.get("start_time"),
                })
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
            st.download_button(
                "📥 Download Execution History JSON",
                data=history_file.read_bytes(),
                file_name="execution_history.json",
                mime="application/json",
            )
        else:
            st.info("Execution history is empty.")
    else:
        st.info("No execution history file found.")

# Tab 2: Downloadable Artifacts
with tab2:
    st.subheader("Generated Machine-Readable Reports")
    
    col1, col2, col3 = st.columns(3)
    
    val_report = settings.REPORTS_DIR / "validation_report.json"
    val_summary_md = settings.REPORTS_DIR / "validation_summary.md"
    db_report = settings.REPORTS_DIR / "database_load_report.json"
    rejections_file = settings.REPORTS_DIR / "rejected_records.json"
    ext_report = settings.REPORTS_DIR / "extraction_report.json"

    with col1:
        st.markdown("**Extraction Report**")
        if ext_report.exists():
            st.download_button("📥 extraction_report.json", data=ext_report.read_bytes(), file_name="extraction_report.json", mime="application/json")
        else:
            st.caption("Not generated yet")

        st.markdown("**Rejected Records**")
        if rejections_file.exists():
            st.download_button("📥 rejected_records.json", data=rejections_file.read_bytes(), file_name="rejected_records.json", mime="application/json")
        else:
            st.caption("Not generated yet")

    with col2:
        st.markdown("**Validation Report (JSON)**")
        if val_report.exists():
            st.download_button("📥 validation_report.json", data=val_report.read_bytes(), file_name="validation_report.json", mime="application/json")
        else:
            st.caption("Not generated yet")

        st.markdown("**Database Load Report**")
        if db_report.exists():
            st.download_button("📥 database_load_report.json", data=db_report.read_bytes(), file_name="database_load_report.json", mime="application/json")
        else:
            st.caption("Not generated yet")

    with col3:
        st.markdown("**Validation Summary (Markdown)**")
        if val_summary_md.exists():
            st.download_button("📥 validation_summary.md", data=val_summary_md.read_bytes(), file_name="validation_summary.md", mime="text/markdown")
        else:
            st.caption("Not generated yet")

    if val_summary_md.exists():
        st.markdown("---")
        st.subheader("📖 Preview: Validation Summary")
        st.markdown(val_summary_md.read_text(encoding="utf-8"))

# Tab 3: Operational Logs
with tab3:
    st.subheader("Live Operational Logs")
    log_file = settings.LOGS_DIR / "streamforge.log"

    if log_file.exists():
        log_filter = st.selectbox("Filter Log Level", ["ALL", "INFO", "WARNING", "ERROR"])
        search_term = st.text_input("Filter Text in Log", value="")

        lines = log_file.read_text(encoding="utf-8", errors="replace").splitlines()
        filtered = []
        for line in lines:
            if log_filter != "ALL" and f"[{log_filter}]" not in line:
                continue
            if search_term and search_term.lower() not in line.lower():
                continue
            filtered.append(line)

        # Show most recent 200 lines
        display_text = "\n".join(filtered[-200:])
        st.text_area("Log Output (Showing up to last 200 lines)", value=display_text, height=400)

        st.download_button(
            "📥 Download Full Log File",
            data=log_file.read_bytes(),
            file_name="streamforge.log",
            mime="text/plain",
        )
    else:
        st.info("No operational log file found at `logs/streamforge.log`.")
