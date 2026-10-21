"""StreamForge Dashboard: Page 4 - Database Explorer."""

from __future__ import annotations

import json
from pathlib import Path
import pandas as pd
from sqlalchemy import text
import streamlit as st

from config.settings import settings
from src.persistence.analytics import DatabaseAnalytics
from src.persistence.connection import get_engine, init_database_schema
from src.persistence.repository import JobRepository

st.set_page_config(page_title="Database Explorer | StreamForge", page_icon="🗄️", layout="wide")

st.title("🗄️ Relational Database Explorer")
st.markdown("Inspect database connection parameters, schema constraints, execute safe analytical queries, and browse stored job listings.")

engine = get_engine()
init_database_schema(engine)
repo = JobRepository(engine)
analytics = DatabaseAnalytics(engine)

# Database Connection Status Banner
with st.container():
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Database Dialect", settings.DATABASE_DIALECT.upper())
    with c2:
        st.metric("Stored Job Records", f"{repo.get_total_count():,}")
    with c3:
        dups = analytics.check_duplicate_fingerprints()
        st.metric("Duplicate Fingerprints", len(dups), delta="Strictly 0" if not dups else "Violation!")

st.caption(f"Connection URL: `{engine.url.render_as_string(hide_password=True)}`")
st.markdown("---")

tab1, tab2, tab3 = st.tabs(["🔍 Search & Filter Listings", "📈 Analytics & Benchmarks", "💻 Safe SQL Console"])

with tab1:
    st.subheader("Filter Stored Job Records")
    f1, f2, f3 = st.columns(3)
    with f1:
        search_kw = st.text_input("Search Keyword (Title / Company)", value="")
    with f2:
        cat_dist = analytics.get_category_distribution()
        all_cats = ["All"] + [c["category"] for c in cat_dist if c["category"]]
        selected_cat = st.selectbox("Category Filter", all_cats)
    with f3:
        top_locs = analytics.get_top_locations(limit=20)
        all_locs = ["All"] + [l["location"] for l in top_locs if l["location"]]
        selected_loc = st.selectbox("Location Filter", all_locs)

    results = analytics.search_listings(
        keyword=search_kw,
        category=selected_cat,
        location=selected_loc,
        limit=100,
    )

    if results:
        df_res = pd.DataFrame(results)
        # Select columns to display
        show_cols = [
            "id", "job_title", "company_name", "category",
            "currency", "salary_min", "salary_max", "salary_avg",
            "location", "employment_type", "posted_date"
        ]
        available_cols = [c for c in show_cols if c in df_res.columns]
        st.dataframe(df_res[available_cols], use_container_width=True, hide_index=True)
        st.caption(f"Showing {len(results)} matching records")
    else:
        st.info("No records matched the filter criteria.")

with tab2:
    st.subheader("Analytical Salary Benchmarks & Distributions")
    col_sal, col_loc = st.columns(2)

    with col_sal:
        st.markdown("**Salary Benchmarks by Currency**")
        sal_bench = analytics.get_salary_benchmarks()
        if sal_bench:
            df_sal = pd.DataFrame(sal_bench)
            st.dataframe(df_sal, use_container_width=True, hide_index=True)
        else:
            st.write("No salary figures available.")

    with col_loc:
        st.markdown("**Top Hiring Locations**")
        loc_data = analytics.get_top_locations(limit=10)
        if loc_data:
            df_loc = pd.DataFrame(loc_data)
            st.dataframe(df_loc, use_container_width=True, hide_index=True)
            st.bar_chart(df_loc.set_index("location")["count"])

with tab3:
    st.subheader("Interactive Safe SQL Query Console")
    st.markdown("Execute read-only `SELECT` queries directly against the database engine.")

    default_query = "SELECT category, count(*) as count, round(avg(salary_avg), 2) as avg_salary FROM job_listings GROUP BY category ORDER BY count DESC;"
    query_input = st.text_area("SQL Query", value=default_query, height=100)
    execute_sql_btn = st.button("▶ Run Query", type="primary")

    if execute_sql_btn and query_input.strip():
        # Enforce read-only constraint for safety
        cleaned_query = query_input.strip()
        first_word = cleaned_query.split()[0].upper()
        if first_word != "SELECT":
            st.error("Only read-only SELECT queries are permitted in this console.")
        else:
            try:
                with engine.connect() as conn:
                    result_df = pd.read_sql_query(text(cleaned_query), conn)
                    st.dataframe(result_df, use_container_width=True)
                    st.caption(f"Query returned {len(result_df)} rows.")
            except Exception as exc:
                st.error(f"SQL execution error: {exc}")
