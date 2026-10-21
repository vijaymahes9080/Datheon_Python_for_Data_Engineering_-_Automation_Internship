"""StreamForge Dashboard: Page 5 - Automation Center."""

from __future__ import annotations

import json
from pathlib import Path
import pandas as pd
import streamlit as st

from config.settings import settings
from src.orchestration.lock import PipelineLock, PipelineLockedException
from src.orchestration.pipeline import ETLPipeline
from src.scheduling.runner import PipelineScheduler

st.set_page_config(page_title="Automation Center | StreamForge", page_icon="⚡", layout="wide")

st.title("⚡ Automation Center & Orchestrator")
st.markdown("Trigger end-to-end ETL pipelines manually, toggle dry-run execution, configure recurring schedules, and observe stage status.")

# Initialize or retrieve scheduler in Streamlit session state
if "scheduler" not in st.session_state:
    st.session_state.scheduler = PipelineScheduler(
        interval_minutes=settings.PIPELINE_SCHEDULE_INTERVAL_MINUTES,
        is_offline=True,
        is_dry_run=False,
    )

scheduler: PipelineScheduler = st.session_state.scheduler

# Sidebar Controls for Pipeline Execution
with st.sidebar:
    st.subheader("⚙️ Pipeline Settings")
    opt_offline = st.toggle("Offline Fixture Mode", value=True, help="Extract from bundled fixtures")
    opt_dry_run = st.toggle("Dry-Run Mode", value=False, help="Simulate pipeline without database writes")
    max_pages = st.slider("Max Pages to Process", min_value=1, max_value=5, value=3)
    record_limit = st.slider("Record Limit", min_value=20, max_value=200, value=120)

    st.markdown("---")
    st.subheader("🚀 Manual Execution")
    run_btn = st.button("▶ Trigger Full ETL Run", type="primary")

# Execute Pipeline on Button Click
if run_btn:
    st.markdown("### 🔄 Pipeline Execution in Progress...")
    progress_bar = st.progress(0)
    status_text = st.empty()

    try:
        with PipelineLock(timeout_seconds=0):
            status_text.text("Acquired lock. Initializing pipeline...")
            progress_bar.progress(10)

            pipeline = ETLPipeline(
                is_offline=opt_offline,
                is_dry_run=opt_dry_run,
                trigger_type="dashboard",
                max_pages=max_pages,
                record_limit=record_limit,
            )

            status_text.text("Executing 8 stages (Extract -> Inspect -> Transform -> Validate -> Upsert -> Verify -> Report -> Notify)...")
            progress_bar.progress(50)

            ctx = pipeline.run()

            progress_bar.progress(100)
            status_text.empty()

            if ctx.status == "SUCCESS":
                mode_str = " (Dry-Run Mode)" if opt_dry_run else ""
                st.success(f"✅ Pipeline run {ctx.execution_id[:8]} completed successfully in {ctx.duration_seconds}s!{mode_str}")
            else:
                st.error(f"❌ Pipeline failed: {ctx.error_message}")

            # Display stage breakdown cards
            cols = st.columns(len(ctx.stages))
            for i, (sname, sdata) in enumerate(ctx.stages.items()):
                with cols[i]:
                    st.metric(sname, sdata.status, delta=f"{sdata.duration_seconds:.2f}s")

    except PipelineLockedException as exc:
        st.warning(f"⚠️ Could not start: {exc}")

st.markdown("---")

# Scheduling & Recurring Automation Controls
st.subheader("⏱️ Background Scheduler Configuration")
st.markdown("StreamForge supports periodic execution using Python `schedule` running safely in a background daemon thread.")

col_sch1, col_sch2 = st.columns(2)

with col_sch1:
    st.markdown("**Scheduler Status**")
    is_sched_active = scheduler.is_running
    if is_sched_active:
        st.success(f"🟢 Scheduler ACTIVE — Running every {scheduler.interval_minutes} minutes.")
    else:
        st.warning("⚪ Scheduler INACTIVE (Manual trigger only).")

    interval = st.number_input(
        "Execution Interval (Minutes)",
        min_value=1,
        max_value=1440,
        value=scheduler.interval_minutes,
        step=5,
    )

with col_sch2:
    st.markdown("**Scheduler Controls**")
    st.caption("Click to start or safely stop background execution. Scheduler never starts unprompted.")
    
    btn_start, btn_stop = st.columns(2)
    with btn_start:
        if st.button("▶ Start Scheduler", disabled=is_sched_active):
            scheduler.interval_minutes = int(interval)
            scheduler.start(run_immediately=False)
            st.rerun()

    with btn_stop:
        if st.button("⏹ Stop Scheduler", disabled=not is_sched_active):
            scheduler.stop()
            st.rerun()

    st.markdown(
        """
        > **Production Deployment Alternatives:**  
        > - **Windows Task Scheduler**: Run `python projects/task_4_automation/run.py` as a scheduled task.  
        > - **Linux Cron**: Add entry `0 * * * * cd /path/to/vj && python projects/task_4_automation/run.py >> logs/cron.log 2>&1`.
        """
    )
