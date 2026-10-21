# StreamForge Setup & Installation Guide

This guide walks through configuring, testing, and running StreamForge on a standard Python workstation.

---

## 1. Prerequisites
- **Python**: Version 3.10, 3.11, or 3.12 (Tested on Python 3.12.10).
- **Git**: Installed and available in PATH.
- **Operating System**: Windows 10/11, macOS, or Linux.
- **Zero External Requirements**: No Docker, paid APIs, cloud credentials, or database servers required.

---

## 2. Installation Steps

### Step 1: Clone or Navigate to the Repository
```bash
git clone git@github.com:vijaymahes9080/Datheon_Python_for_Data_Engineering_-_Automation_Internship.git
cd Datheon_Python_for_Data_Engineering_-_Automation_Internship
```

### Step 2: Create and Activate Virtual Environment (Optional but recommended)
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate
```

### Step 3: Install Required Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
# On Windows PowerShell:
Copy-Item .env.example .env
# On Linux/macOS:
cp .env.example .env
```
Default configuration uses local SQLite (`database/streamforge.db`) and console alerting.

---

## 3. Launching the Streamlit Operations Dashboard
```bash
streamlit run app.py
```
Open your browser to the URL displayed in the terminal (typically `http://localhost:8501`).

---

## 4. Running Independent Task CLI Entry Points

```bash
# Task 1: Autonomous Web Scraper & Extractor (Offline fixture mode)
python projects/task_1_extraction/run.py --offline

# Task 2: Automated Data Cleaning & Schema Transformation
python projects/task_2_quality/run.py

# Task 3: Relational Persistence & Upsert Engine
python projects/task_3_persistence/run.py --test-rollback

# Task 4: End-to-End Orchestrated ETL Pipeline (Dry-run mode)
python projects/task_4_automation/run.py --dry-run

# Task 4: End-to-End Orchestrated ETL Pipeline (Live mode)
python projects/task_4_automation/run.py
```

---

## 5. Running the Test Suite
```bash
pytest tests/ -v
```
All unit and integration tests run offline without network access.
