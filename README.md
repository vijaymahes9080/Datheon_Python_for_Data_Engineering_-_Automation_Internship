# StreamForge — Intelligent Data Extraction, Quality Engineering, Database Integration & Workflow Automation

**Person 3 Internship Implementation**

StreamForge is an enterprise data engineering and automation suite featuring an autonomous web scraper, an automated data cleaning and schema transformation engine, an idempotent relational database auto-ingestion engine, and a scheduled end-to-end ETL orchestrator with alerting, unified by a central Streamlit data operations dashboard.

---

## Directory Layout

```text
streamforge_etl/
├── app.py                             # Central Streamlit Dashboard
├── requirements.txt                   # Project dependencies
├── README.md                          # Documentation
├── .gitignore                         # Git exclusion rules
├── .env.example                       # Environment configuration template
├── config/                            # Settings & Schema rules
├── data/
│   ├── raw/                           # Raw extracted files
│   ├── processed/                     # Cleaned & transformed datasets
│   └── fixtures/                      # Bundled HTML & mock datasets
├── database/                          # SQLite persistent database
├── docs/                              # Architecture, schemas, guides
├── logs/                              # Rotating runtime execution logs
├── projects/                          # 4 Independent Task CLI entry points
│   ├── task_1_extraction/
│   ├── task_2_quality/
│   ├── task_3_persistence/
│   └── task_4_automation/
├── reports/                           # Validation, load & execution reports
├── src/                               # Modular ETL Python packages
│   ├── extraction/
│   ├── quality/
│   ├── persistence/
│   ├── orchestration/
│   ├── scheduling/
│   ├── notifications/
│   └── reporting/
└── tests/                             # Automated test suite (Pytest)
    ├── unit/
    ├── integration/
    └── fixtures/
```

---

## Quick Start Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Launch the Streamlit Dashboard
streamlit run app.py

# Run Independent Task CLIs
python projects/task_1_extraction/run.py --offline
python projects/task_2_quality/run.py
python projects/task_3_persistence/run.py
python projects/task_4_automation/run.py --dry-run
python projects/task_4_automation/run.py

# Run Automated Tests
pytest tests/ -v
```
