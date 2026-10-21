# StreamForge Schema Reference & Data Contract

This document outlines the data contracts, validation rules, field invariants, and database DDL specifications for StreamForge.

---

## 1. Relational Schema (`job_listings`)

| Column Name | SQL Type | Constraints | Description |
|:---|:---|:---|:---|
| `id` | `INTEGER` | Primary Key, Auto-increment | Unique internal surrogate identifier |
| `fingerprint_hash` | `VARCHAR(64)` | Unique, Not Null, Indexed | Deterministic SHA-256 natural key used for idempotent upserts |
| `job_title` | `VARCHAR(255)` | Not Null, Indexed | Standardized position title |
| `company_name` | `VARCHAR(255)` | Not Null, Indexed | Employing organization or seller name |
| `salary_raw` | `VARCHAR(255)` | Nullable | Original unparsed salary string |
| `salary_min` | `NUMERIC(12,2)` | Nullable, Check `>= 0` | Lower bound of compensation range |
| `salary_max` | `NUMERIC(12,2)` | Nullable, Check `>= salary_min` | Upper bound of compensation range |
| `salary_avg` | `NUMERIC(12,2)` | Nullable | Midpoint arithmetic average compensation |
| `currency` | `VARCHAR(10)` | Nullable, Default `'USD'` | ISO 4217 standard currency code (`USD`, `EUR`, `GBP`, `CAD`, `INR`) |
| `location` | `VARCHAR(255)` | Default `'Unspecified'` | Normalized city, country or remote classification |
| `category` | `VARCHAR(100)` | Default `'General'` | Job domain classification |
| `employment_type` | `VARCHAR(50)` | Default `'Full-time'` | Standardized employment engagement (`Full-time`, `Contract`, etc.) |
| `posted_date` | `VARCHAR(20)` | Nullable, Indexed | ISO-8601 publication date (`YYYY-MM-DD`) |
| `source_url` | `TEXT` | Not Null | Fully qualified canonical source link |
| `created_at` | `TIMESTAMP` | Server Default `NOW()` | Initial ingestion timestamp |
| `updated_at` | `TIMESTAMP` | Server Default `NOW()`, onupdate | Most recent update timestamp |

### Indexes
1. `idx_jobs_category_location` ON `job_listings(category, location)` — composite index accelerating multi-attribute filtering.
2. `idx_jobs_currency_salary` ON `job_listings(currency, salary_avg)` — composite index for salary benchmarking.
3. B-Tree indexes on `posted_date`, `company_name`, and `job_title`.

---

## 2. Pipeline Execution Audit Schema (`pipeline_executions`)

| Column Name | SQL Type | Description |
|:---|:---|:---|
| `id` | `INTEGER` | Primary key |
| `execution_id` | `VARCHAR(64)` | UUIDv4 identifier per pipeline run |
| `trigger_type` | `VARCHAR(50)` | Execution initiator (`cli`, `dashboard`, `scheduled`) |
| `is_dry_run` | `BOOLEAN` | True if run without database writes |
| `status` | `VARCHAR(50)` | `SUCCESS`, `FAILED`, `RUNNING` |
| `start_time` | `TIMESTAMP` | UTC start timestamp |
| `end_time` | `TIMESTAMP` | UTC completion timestamp |
| `duration_seconds` | `FLOAT` | Total runtime in seconds |
| `records_extracted` | `INTEGER` | Number of raw extracted items |
| `records_cleaned` | `INTEGER` | Number of validated items |
| `records_inserted` | `INTEGER` | New rows added to database |
| `records_updated` | `INTEGER` | Existing rows updated on conflict |
| `records_rejected` | `INTEGER` | Discarded rows violating validation |
| `error_message` | `TEXT` | Stack trace or failure description |

---

## 3. Data Quality Invariants & Rejection Rules
- **Missing Required Fields**: Any record lacking `job_title`, `company_name`, or `source_url` is rejected into `reports/rejected_records.json`.
- **Invalid Dates**: Corrupted text strings (`"INVALID_DATE"`) or future dates (`> today + 1 day`) are rejected. Missing dates default to extraction date.
- **Inverted Ranges**: Salary ranges where `salary_min > salary_max` trigger immediate validation rejection.
- **Currency Isolation**: Currencies are never converted or combined into a single denomination without verified exchange rates.
