# StreamForge — Internship Evaluator Demonstration Guide

A concise script and walkthrough for demonstrating StreamForge during evaluation and technical interviews.

---

## 1. Project Identity & Overview (30 Seconds)
- **Name**: **StreamForge: Intelligent Data Extraction, Quality Engineering, Database Integration & Workflow Automation**.
- **Role**: Person 3 Independent Implementation.
- **Core Pillars**:
  1. Autonomous Web Extraction with backoff and fingerprint deduplication.
  2. Data Quality & Schema Validation with currency/date normalization and rejection ledgers.
  3. Relational Persistence with dialect-aware idempotent upserts and rollback safety.
  4. Scheduled Orchestration with concurrency locking and multi-channel alerting.
  5. Modern Streamlit Data Operations Dashboard.

---

## 2. Live Demonstration Flow (5 Minutes)

### Step 1: Run Full Pytest Suite
Show that all unit and integration tests pass cleanly:
```bash
pytest tests/ -v
```
*Expected: 34+ tests passing covering extraction, quality, persistence, and orchestration.*

### Step 2: Demonstrate Task 1 (Web Scraper & 100+ Records)
```bash
python projects/task_1_extraction/run.py --offline
```
*Key highlight*: Extracts 120 unique records across 3 paginated HTML pages with 0 errors and writes `data/raw/extracted_jobs.csv` and `data/raw/extracted_jobs.json`.

### Step 3: Demonstrate Task 2 (Data Quality & Rejection Ledger)
```bash
python projects/task_2_quality/run.py
```
*Key highlight*: Shows snake_case standardization, currency range parsing without cross-currency contamination, ISO date normalization, and segregating corrupted/future dates and duplicates into `reports/rejected_records.json`.

### Step 4: Demonstrate Task 3 (Idempotent Database Upserts)
```bash
python projects/task_3_persistence/run.py --test-rollback
```
*Key highlight*: Ingests records on first pass; executes second pass and proves 0 records inserted (100% updated), confirming strict idempotence. Confirms atomic transaction rollback on simulated fault.

### Step 5: Demonstrate Task 4 (End-to-End Orchestrated Pipeline)
```bash
python projects/task_4_automation/run.py --dry-run
python projects/task_4_automation/run.py
```
*Key highlight*: Shows 8-stage execution state machine (**Extract -> Inspect -> Transform -> Validate -> Upsert -> Verify -> Report -> Notify**), concurrency lock, and console alerting.

### Step 6: Interactive Dashboard Tour
```bash
streamlit run app.py
```
*Tour sequence*:
1. **Overview**: Point to live KPI telemetry and real database count.
2. **Extraction Studio**: Demonstrate offline extraction toggle and CSV/JSON downloads.
3. **Quality Inspector**: Show before-and-after profiling comparison and rejection ledger.
4. **Database Explorer**: Run search queries and test the safe SQL console.
5. **Automation Center**: Trigger a pipeline execution from the UI and demonstrate the background scheduler toggle.
6. **Reports & Logs**: View execution history and live rotating logs.
