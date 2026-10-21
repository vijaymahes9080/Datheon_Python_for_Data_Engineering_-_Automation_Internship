# StreamForge Data Quality & Validation Summary

**Execution Timestamp:** `2026-10-21T11:37:40.838315+00:00`  
**Overall Validation Status:** **PASS**

---

## 1. Quality Metrics Overview

| Metric | Value |
|:---|:---|
| **Total Input Records** | `3` |
| **Accepted Clean Records** | `2` |
| **Rejected Records** | `1` |
| **Duplicates Eliminated** | `0` |
| **Data Acceptance Rate** | `66.67%` |

---

## 2. Rejection Reasons Breakdown

| Violation / Cause | Frequency |
|:---|:---|
| Missing title | 1 |

---

## 3. Data Transformations Applied
- **Snake_case Standardization**: Mapped inconsistent column names to canonical schema.
- **Whitespace Normalization**: Removed leading/trailing spaces and collapsed duplicate internal spaces.
- **Currency & Salary Parsing**: Extracted currency codes without silent cross-currency conversion; parsed min/max/avg numbers.
- **Date Normalization**: Standardized diverse formats (`DD/MM/YYYY`, relative days) to ISO-8601 (`YYYY-MM-DD`).
- **Defensive Rejection**: Flagged future dates and missing required fields into `rejected_records.json`.
