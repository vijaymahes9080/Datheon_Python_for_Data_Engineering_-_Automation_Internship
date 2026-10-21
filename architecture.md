# StreamForge Architecture & System Specification

## 1. System Overview
**StreamForge** is an enterprise data engineering, extraction, and automated ETL suite designed as an independent implementation for Person 3. The architecture adheres to clean separation of concerns, defensive data validation, idempotent data persistence, resilient orchestration, and modern data observability.

```text
+-----------------------------------------------------------------------------------+
|                                  StreamForge                                      |
+-----------------------------------------------------------------------------------+
|                                                                                   |
|  [Task 1: Extractor]   ==>  [Task 2: Quality Engine]  ==>  [Task 3: Persistence]  |
|  - BS4 & Requests            - Snake_case normalization     - SQLAlchemy 2.0      |
|  - Exponential Backoff       - Currency/Salary parser       - SQLite (default)    |
|  - Deduplication Fingerprint - ISO Date parser              - PostgreSQL ready    |
|  - HTML Fixture Engine       - Pydantic schema validation   - Idempotent upsert   |
|  - CSV/JSON raw exports      - Rejection ledger             - Atomic rollback     |
|                                                                                   |
|                                         ^                                         |
|                                         | Orchestrated by                         |
|                                         v                                         |
|  [Task 4: Pipeline Automation & Orchestrator]                                     |
|  - Sequential State Machine: Extract -> Inspect -> Transform -> Upsert -> Alert   |
|  - Concurrency Lock, Unique Execution UUID, Dry-Run Mode                         |
|  - Rotating File Logging & Multi-Channel Alerting (Console / SMTP / Webhook)      |
|                                                                                   |
|                                         ^                                         |
|                                         | Visualized through                      |
|                                         v                                         |
|  [Central Streamlit Data Operations Dashboard (6 Pages)]                          |
|  - Light / Deep Navy Minimalist Design, Real DB Metrics, Live Execution Controls   |
+-----------------------------------------------------------------------------------+
```

## 2. Core Modules & Responsibilities

### `src.extraction` (Task 1)
- **`HTTPClient`**: Safe requests with session pooling, standard User-Agent header, timeouts, and exponential backoff retry policy (`1s`, `2s`, `4s` jittered).
- **`HTMLParser`**: BeautifulSoup4 parser with defensive DOM selectors capable of extracting 8 core attributes without crashing on missing tags.
- **`Scraper`**: Pagination engine traversing URL queries and `rel="next"` tags, generating SHA-256 fingerprint hashes to prevent duplicate ingestion.
- **Offline Mode**: Uses local fixtures in `data/fixtures/html/` with 100+ synthetic records to ensure 100% offline reproducibility.

### `src.quality` (Task 2)
- **`Cleaner`**: Normalizes column names into strict `snake_case`, strips invisible whitespace, converts whitespace-only cells to genuine nulls.
- **`Parsers`**:
  - Currency Parser: Extracts ISO currency codes (`USD`, `EUR`, `GBP`, `CAD`, `INR`), parses ranges and numbers (`$120,000 - $150,000` -> min/max/midpoint), preserves original raw string.
  - Date Parser: Normalizes messy dates (`DD/MM/YYYY`, `MM-DD-YYYY`, `ISO`, relative strings) to ISO-8601 `YYYY-MM-DD`, marking corrupted/invalid dates for rejection.
- **`Validator`**: Validates rows against schema rules. Segregates clean records to `data/processed/` and invalid rows to `reports/rejected_records.json`.
- **`Profiler`**: Produces comprehensive before-and-after quality comparison reports in JSON and Markdown.

### `src.persistence` (Task 3)
- **`Models`**: SQLAlchemy 2.0 declarative schema with explicit primary key, unique constraints (`fingerprint_hash`), check constraints, and composite indexes (`(category, location)`).
- **`Repository`**: Dialect-aware idempotent upserting (`sqlite_upsert` and `postgresql_upsert`), batching, transaction rollback on failures, recording `inserted`, `updated`, `unchanged`, and `failed` counts.
- **`Analytics`**: Verification queries for deduplication audits, category distributions, and salary statistics.

### `src.orchestration` (Task 4)
- **`Pipeline`**: Sequential execution coordinator tracking stage status, execution duration, and errors.
- **`Lock`**: File-based concurrency lock preventing overlapping runs.
- **`Notifier`**: Alerting service supporting Console, SMTP, and Webhook dispatch without exposing credentials.
- **`Scheduler`**: Configurable scheduler using Python `schedule`.

## 3. Data Integrity & Reproducibility Guarantees
1. **Idempotence**: Running the ETL pipeline multiple times on the same dataset results in 0 duplicate records.
2. **Non-Destructive Operations**: Raw inputs are preserved unchanged; processed data is written to versioned artifacts.
3. **No Fake Metrics**: All metrics displayed in reports and dashboards originate directly from database queries or runtime logs.
