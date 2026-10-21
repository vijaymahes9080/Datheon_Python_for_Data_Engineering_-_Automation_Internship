# StreamForge Troubleshooting & Diagnostic Guide

Common troubleshooting scenarios and recovery procedures.

---

## 1. Concurrency Lock Errors (`PipelineLockedException`)

### Symptom:
```text
PipelineLockedException: Another pipeline execution is currently in progress. Lock file: logs/pipeline.lock
```

### Cause:
A previous pipeline execution terminated abruptly (e.g. process was killed) while holding the lock file, or another terminal/scheduler is actively running.

### Remedy:
1. Verify no background Python processes are running the pipeline:
   ```bash
   # On Windows:
   Get-Process python
   ```
2. If confirmed inactive, remove the stale lock file:
   ```bash
   # On Windows:
   Remove-Item logs/pipeline.lock -Force
   # On Linux/macOS:
   rm -f logs/pipeline.lock
   ```

---

## 2. SQLite Database File Lock (`database is locked`)

### Symptom:
```text
sqlite3.OperationalError: database is locked
```

### Cause:
Multiple concurrent connections writing to SQLite simultaneously with insufficient timeout.

### Remedy:
`src/persistence/connection.py` configures `connect_args={"check_same_thread": False, "timeout": 30}` to prevent write contention. Ensure that connections are opened via the `get_session()` context manager which guarantees automatic session closure.

---

## 3. Missing Output Files / Artifacts

### Symptom:
`FileNotFoundError: data/raw/extracted_jobs.csv` or `data/processed/cleaned_jobs.csv`.

### Remedy:
Execute tasks in order:
```bash
python projects/task_1_extraction/run.py --offline
python projects/task_2_quality/run.py
python projects/task_3_persistence/run.py
```
Or execute Task 4 to run the entire sequence automatically:
```bash
python projects/task_4_automation/run.py
```

---

## 4. Date Normalization Issues

### Symptom:
Rows rejected with `Date validation failure`.

### Remedy:
StreamForge intentionally flags corrupted or unparseable date strings into `reports/rejected_records.json` instead of silently inserting inaccurate timestamps. Check `reports/rejected_records.json` to review the rejected rows and causes.
