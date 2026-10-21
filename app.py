"""StreamForge Central Data Operations Dashboard.

Identity: Light, minimalist data operations interface with deep navy navigation,
electric cyan accents, clean typography, and real-time backend metric telemetry.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
import streamlit as st

# Ensure package root is in sys.path
PACKAGE_ROOT = Path(__file__).resolve().parent
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from config.settings import settings
from src.persistence.analytics import DatabaseAnalytics
from src.persistence.connection import get_engine, init_database_schema
from src.persistence.repository import JobRepository

# Page Configuration
st.set_page_config(
    page_title="StreamForge | Data Engineering Suite",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Design System CSS
st.markdown(
    """
    <style>
    /* Global Styles */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Primary Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #0F172A;
        color: #F8FAFC;
    }
    section[data-testid="stSidebar"] .stMarkdown h1, 
    section[data-testid="stSidebar"] .stMarkdown h2, 
    section[data-testid="stSidebar"] .stMarkdown h3 {
        color: #38BDF8 !important;
    }
    section[data-testid="stSidebar"] a {
        color: #E2E8F0 !important;
    }
    
    /* Metric Cards */
    div[data-testid="metric-container"] {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 16px 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        border-left: 4px solid #0EA5E9;
    }
    div[data-testid="metric-container"] label {
        color: #64748B !important;
        font-size: 0.85rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        color: #0F172A !important;
        font-size: 1.8rem;
        font-weight: 700;
        font-family: 'JetBrains Mono', monospace;
    }
    
    /* Tables & DataFrames */
    .stDataFrame {
        border: 1px solid #E2E8F0;
        border-radius: 6px;
    }
    
    /* Pill Badges */
    .status-badge-success {
        background-color: #ECFDF5;
        color: #059669;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 600;
        border: 1px solid #A7F3D0;
    }
    .status-badge-dry {
        background-color: #EFF6FF;
        color: #2563EB;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 600;
        border: 1px solid #BFDBFE;
    }
    
    /* Buttons */
    .stButton>button {
        background-color: #0284C7;
        color: #FFFFFF;
        font-weight: 600;
        border-radius: 6px;
        border: none;
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        background-color: #0369A1;
        color: #FFFFFF;
        box-shadow: 0 2px 4px rgba(14, 165, 233, 0.2);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Sidebar Identity
with st.sidebar:
    st.markdown("### ⚡ StreamForge")
    st.caption("Data Engineering & Workflow Automation")
    st.markdown("---")
    st.markdown(
        """
        **System Architecture**
        - 🌐 Task 1: Autonomous Web Extractor
        - ✨ Task 2: Data Quality & Schema Engine
        - 🗄️ Task 3: Relational Persistence Engine
        - ⚡ Task 4: Scheduled ETL Orchestrator
        """
    )
    st.markdown("---")
    st.caption("Person 3 Internship Implementation")
    st.caption(f"Environment: `{settings.ENVIRONMENT.upper()}`")
    st.caption(f"Engine: `{settings.DATABASE_DIALECT.upper()}`")

# Main View
st.title("⚡ StreamForge Command Center")
st.markdown(
    "Welcome to **StreamForge**, a data extraction, quality engineering, and workflow automation platform. "
    "Use the left sidebar navigation to explore dedicated workspaces for each task."
)

# Initialize Database Schema if not present
engine = get_engine()
init_database_schema(engine)
repo = JobRepository(engine)
analytics = DatabaseAnalytics(engine)

# Telemetry Overview KPI Cards
col1, col2, col3, col4 = st.columns(4)

total_db_records = repo.get_total_count()
duplicate_check = analytics.check_duplicate_fingerprints()

history_file = settings.REPORTS_DIR / "execution_history.json"
executions = []
if history_file.exists():
    try:
        executions = json.loads(history_file.read_text(encoding="utf-8"))
    except Exception:
        executions = []

last_exec = executions[0] if executions else {}
last_status = last_exec.get("status", "NO RUNS")
last_duration = f"{last_exec.get('duration_seconds', 0.0):.2f}s" if last_exec else "N/A"

with col1:
    st.metric("Database Listings", f"{total_db_records:,}", delta="Verified Records")
with col2:
    st.metric("Latest Pipeline Run", last_status, delta=last_duration)
with col3:
    st.metric("Data Integrity Duplicates", len(duplicate_check), delta="0 Duplicates" if not duplicate_check else "Violation")
with col4:
    st.metric("Total Execution Runs", len(executions), delta="Persistent Audit")

st.markdown("---")

# Quick Navigation Grid
st.subheader("🛠️ Dedicated Workspaces")
c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("#### 📊 [1. Overview](Overview)")
    st.write("Examine execution history, health monitors, throughput, and system status.")
    
    st.markdown("#### 🌐 [2. Extraction Studio](Extraction_Studio)")
    st.write("Configure live or offline extraction, pagination, inspect raw data and download CSV/JSON.")

with c2:
    st.markdown("#### ✨ [3. Quality Inspector](Quality_Inspector)")
    st.write("Column profiling, missing-value imputation, date & currency normalization, and rejection ledgers.")
    
    st.markdown("#### 🗄️ [4. Database Explorer](Database_Explorer)")
    st.write("Schema inspection, SQL verification queries, aggregations, and live table browser.")

with c3:
    st.markdown("#### ⚡ [5. Automation Center](Automation_Center)")
    st.write("Trigger live or dry-run ETL pipelines, configure recurring schedules, and monitor background threads.")
    
    st.markdown("#### 📜 [6. Reports & Logs](Reports_and_Logs)")
    st.write("Download machine-readable validation reports, inspection summaries, and search rotating logs.")

st.markdown("---")

# Recent Pipeline Executions Table
st.subheader("🕒 Recent Operational Telemetry")
if executions:
    display_rows = []
    for ex in executions[:8]:
        display_rows.append({
            "Execution ID": ex.get("execution_id", "")[:8],
            "Trigger": ex.get("trigger_type", "manual"),
            "Mode": "Dry Run" if ex.get("is_dry_run") else "Live",
            "Status": ex.get("status", "UNKNOWN"),
            "Duration": f"{ex.get('duration_seconds', 0.0):.2f}s",
            "Extracted": ex.get("record_counts", {}).get("extracted", 0),
            "Cleaned": ex.get("record_counts", {}).get("cleaned", 0),
            "Inserted": ex.get("record_counts", {}).get("inserted", 0),
            "Start Time": ex.get("start_time", "")[:19].replace("T", " "),
        })
    st.dataframe(pd.DataFrame(display_rows), use_container_width=True, hide_index=True)
else:
    st.info("No pipeline executions recorded yet. Run Task 4 or visit the Automation Center to trigger a run.")
