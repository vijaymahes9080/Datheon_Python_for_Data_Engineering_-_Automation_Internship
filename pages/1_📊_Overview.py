"""StreamForge Dashboard: Page 1 - Overview."""

from __future__ import annotations

import json
from pathlib import Path
import pandas as pd
import streamlit as st

from config.settings import settings
from src.persistence.analytics import DatabaseAnalytics
from src.persistence.connection import get_engine
from src.persistence.repository import JobRepository

st.set_page_config(page_title="Overview | StreamForge", page_icon="📊", layout="wide")

st.title("📊 System Overview & Operations Telemetry")
st.markdown("Real-time monitoring of pipeline executions, record velocity, and relational storage integrity.")

engine = get_engine()
repo = JobRepository(engine)
analytics = DatabaseAnalytics(engine)

# Load execution history
history_file = settings.REPORTS_DIR / "execution_history.json"
executions = []
if history_file.exists():
    try:
        executions = json.loads(history_file.read_text(encoding="utf-8"))
    except Exception:
        executions = []

# Top Row Metrics
c1, c2, c3, c4 = st.columns(4)

total_records = repo.get_total_count()
latest_run = executions[0] if executions else {}
status = latest_run.get("status", "NO RUNS")
duration = f"{latest_run.get('duration_seconds', 0.0):.2f}s" if latest_run else "N/A"
extracted_last = latest_run.get("record_counts", {}).get("extracted", 0) if latest_run else 0

with c1:
    st.metric("Total DB Listings", f"{total_records:,}")
with c2:
    st.metric("Last Run Status", status, delta=duration)
with c3:
    st.metric("Extracted in Last Run", f"{extracted_last:,}")
with c4:
    st.metric("Total Historic Executions", len(executions))

st.markdown("---")

# Execution Status Breakdown & Category Distribution
col_left, col_right = st.columns([3, 2])

with col_left:
    st.subheader("📈 Recent Execution Timeline")
    if executions:
        rows = []
        for e in executions[:15]:
            rows.append({
                "Execution ID": e.get("execution_id", "")[:8],
                "Trigger": e.get("trigger_type", "manual"),
                "Mode": "Dry Run" if e.get("is_dry_run") else "Live",
                "Status": e.get("status"),
                "Duration (s)": e.get("duration_seconds", 0.0),
                "Extracted": e.get("record_counts", {}).get("extracted", 0),
                "Cleaned": e.get("record_counts", {}).get("cleaned", 0),
                "Inserted": e.get("record_counts", {}).get("inserted", 0),
                "Updated": e.get("record_counts", {}).get("updated", 0),
            })
        df_exec = pd.DataFrame(rows)
        st.dataframe(df_exec, use_container_width=True, hide_index=True)
    else:
        st.info("No executions recorded. Run a pipeline from the Automation Center.")

with col_right:
    st.subheader("🏷️ Stored Listings by Category")
    cats = analytics.get_category_distribution()
    if cats:
        df_cats = pd.DataFrame(cats)
        st.dataframe(df_cats, use_container_width=True, hide_index=True)
        st.bar_chart(df_cats.set_index("category")["total_jobs"])
    else:
        st.info("No records stored in database yet.")

st.markdown("---")

# Verification & Integrity Status
st.subheader("🛡️ Storage & Ingestion Invariants")
v1, v2, v3 = st.columns(3)

dup_check = analytics.check_duplicate_fingerprints()
sal_check = analytics.get_salary_benchmarks()

with v1:
    st.markdown("**Duplicate Key Audit**")
    if not dup_check:
        st.success("✅ 0 duplicate fingerprints detected. Table strictly idempotent.")
    else:
        st.error(f"❌ {len(dup_check)} duplicate fingerprints detected!")

with v2:
    st.markdown("**Database Dialect & Engine**")
    st.info(f"Connected to `{engine.url.render_as_string(hide_password=True)}`")

with v3:
    st.markdown("**Currency Isolation Integrity**")
    if sal_check:
        currencies = [s["currency"] for s in sal_check]
        st.success(f"✅ Isolated currencies maintained: {', '.join(currencies)}")
    else:
        st.write("No salary records ingested.")
