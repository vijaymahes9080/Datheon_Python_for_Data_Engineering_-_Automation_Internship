"""StreamForge Dashboard: Page 3 - Quality Inspector."""

from __future__ import annotations

import json
from pathlib import Path
import pandas as pd
import streamlit as st

from config.settings import settings
from src.quality.cleaner import DataCleaner
from src.quality.profiler import QualityProfiler
from src.quality.validator import SchemaValidator

st.set_page_config(page_title="Quality Inspector | StreamForge", page_icon="✨", layout="wide")

st.title("✨ Quality Inspector & Transformation Lab")
st.markdown("Profile source datasets, audit missing values, standardize columns, normalize dates and currencies, and review rejection ledgers.")

# Dataset Selection / Upload
with st.sidebar:
    st.subheader("📁 Dataset Source")
    dataset_choice = st.radio(
        "Select Dataset to Inspect",
        ["Messy Fixture (raw_mock_jobs.csv)", "Raw Extracted (extracted_jobs.csv)", "Upload Custom CSV"],
    )

    df_to_inspect: pd.DataFrame | None = None
    if dataset_choice == "Messy Fixture (raw_mock_jobs.csv)":
        p = settings.DATA_FIXTURES_DIR / "raw_mock_jobs.csv"
        if p.exists():
            df_to_inspect = pd.read_csv(p)
    elif dataset_choice == "Raw Extracted (extracted_jobs.csv)":
        p = settings.DATA_RAW_DIR / "extracted_jobs.csv"
        if p.exists():
            df_to_inspect = pd.read_csv(p)
    else:
        uploaded = st.file_uploader("Upload CSV", type=["csv"])
        if uploaded:
            df_to_inspect = pd.read_csv(uploaded)

    st.markdown("---")
    st.subheader("⚙️ Quality Controls")
    enable_dedup = st.checkbox("Deduplicate on Fingerprint", value=True)
    run_quality_btn = st.button("✨ Run Cleaning & Validation", type="primary")

# Execute Cleaning & Validation
if run_quality_btn and df_to_inspect is not None:
    with st.spinner("Executing data quality rules and transformations..."):
        # 1. Clean
        cleaned_df, clean_meta = DataCleaner.clean(df_to_inspect)
        # 2. Validate
        valid_df, rejections, summary = SchemaValidator.validate_dataset(cleaned_df, deduplicate=enable_dedup)
        # 3. Profile
        report = QualityProfiler.generate_comparison_report(
            raw_df=df_to_inspect,
            cleaned_df=valid_df,
            rejected_records=rejections,
            validation_summary=summary,
            cleaning_metadata=clean_meta,
        )
        # Save output
        out_csv = settings.DATA_PROCESSED_DIR / "cleaned_jobs.csv"
        valid_df.to_csv(out_csv, index=False)
        st.success(f"Processing complete: {len(valid_df)} accepted, {len(rejections)} rejected.")

# Load latest validation report
val_report_path = settings.REPORTS_DIR / "validation_report.json"
rejections_path = settings.REPORTS_DIR / "rejected_records.json"
processed_csv = settings.DATA_PROCESSED_DIR / "cleaned_jobs.csv"

if val_report_path.exists():
    try:
        report_data = json.loads(val_report_path.read_text(encoding="utf-8"))
    except Exception:
        report_data = {}

    summary = report_data.get("summary", {})
    
    # KPI metrics row
    k1, k2, k3, k4, k5 = st.columns(5)
    with k1:
        st.metric("Input Records", summary.get("input_record_count", 0))
    with k2:
        st.metric("Accepted Clean", summary.get("output_clean_record_count", 0))
    with k3:
        st.metric("Rejected Rows", summary.get("rejected_record_count", 0))
    with k4:
        st.metric("Duplicates Dropped", summary.get("duplicates_removed", 0))
    with k5:
        st.metric("Acceptance Rate", f"{summary.get('acceptance_rate_pct', 0.0)}%")

    st.markdown("---")

    # Before and After Comparison Tabs
    tab1, tab2, tab3 = st.tabs(["📊 Quality Profiling Comparison", "✅ Accepted Clean Dataset", "🚫 Rejection Ledger"])

    with tab1:
        st.subheader("Before-and-After Profiling")
        b_prof = report_data.get("before_profile", {}).get("columns", {})
        a_prof = report_data.get("after_profile", {}).get("columns", {})

        cols_compare = []
        for col_name, b_meta in b_prof.items():
            cols_compare.append({
                "Column (Raw)": col_name,
                "Raw Dtype": b_meta.get("dtype"),
                "Raw Null Count": b_meta.get("null_count"),
                "Raw Null %": f"{b_meta.get('null_percentage')}%",
                "Raw Unique": b_meta.get("unique_values"),
            })
        st.markdown("**Raw Input Profile**")
        st.dataframe(pd.DataFrame(cols_compare), use_container_width=True, hide_index=True)

        st.markdown("**Rejection Breakdown by Cause**")
        reasons_dict = report_data.get("rejection_reasons_breakdown", {})
        if reasons_dict:
            st.bar_chart(pd.Series(reasons_dict))
        else:
            st.success("No rejected rows!")

    with tab2:
        st.subheader("Cleaned & Validated Records")
        if processed_csv.exists():
            df_clean = pd.read_csv(processed_csv)
            st.dataframe(df_clean, use_container_width=True, hide_index=True)
            st.download_button(
                "📥 Download Cleaned CSV",
                data=processed_csv.read_bytes(),
                file_name="cleaned_jobs.csv",
                mime="text/csv",
            )
        else:
            st.info("Cleaned CSV not generated yet.")

    with tab3:
        st.subheader("Rejected Records Ledger")
        if rejections_path.exists():
            try:
                rej_data = json.loads(rejections_path.read_text(encoding="utf-8"))
            except Exception:
                rej_data = []

            if rej_data:
                rej_rows = []
                for item in rej_data:
                    rej_rows.append({
                        "Row #": item.get("row_index"),
                        "Job Title": item.get("record", {}).get("job_title", "N/A"),
                        "Company": item.get("record", {}).get("company_name", "N/A"),
                        "Rejection Reasons": "; ".join(item.get("reasons", [])),
                    })
                st.dataframe(pd.DataFrame(rej_rows), use_container_width=True, hide_index=True)
            else:
                st.success("Zero records were rejected.")
        else:
            st.info("No rejection ledger file found.")

elif df_to_inspect is not None:
    st.subheader("📋 Dataset Preview")
    st.dataframe(df_to_inspect, use_container_width=True, hide_index=True)
    st.info("Click 'Run Cleaning & Validation' in the sidebar to process this dataset.")
else:
    st.info("Select or upload a dataset using the sidebar to begin inspecting data quality.")
