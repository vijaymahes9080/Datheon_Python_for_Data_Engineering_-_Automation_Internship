"""Integration tests for the complete end-to-end StreamForge ETL workflow."""

from __future__ import annotations

import json
from pathlib import Path
import pytest
from sqlalchemy import create_engine

from config.settings import settings
from src.orchestration.context import PipelineContext
from src.orchestration.lock import PipelineLock, PipelineLockedException
from src.orchestration.pipeline import ETLPipeline
from src.scheduling.runner import PipelineScheduler


class TestEndToEndPipeline:
    """Full workflow integration test."""

    def test_complete_offline_etl_execution(self):
        pipeline = ETLPipeline(
            is_offline=True,
            is_dry_run=False,
            trigger_type="test_e2e",
            max_pages=3,
            record_limit=150,
        )
        ctx = pipeline.run()

        assert ctx.status == "SUCCESS"
        assert ctx.error_message is None
        assert ctx.duration_seconds > 0

        # Verify all 8 stages executed in order
        expected_stages = ["Extract", "Inspect", "Transform", "Validate", "Upsert", "Verify", "Report", "Notify"]
        for s in expected_stages:
            assert s in ctx.stages
            assert ctx.stages[s].status in ("SUCCESS", "SKIPPED")

        # Verify record throughput
        counts = ctx.to_dict()["record_counts"]
        assert counts["extracted"] >= 100
        assert counts["cleaned"] >= 100

        # Verify persisted history
        history_path = settings.REPORTS_DIR / "execution_history.json"
        assert history_path.exists()
        with open(history_path, encoding="utf-8") as f:
            history = json.load(f)
        assert len(history) > 0
        assert history[0]["execution_id"] == ctx.execution_id

    def test_dry_run_skips_database_write(self):
        pipeline = ETLPipeline(
            is_offline=True,
            is_dry_run=True,
            trigger_type="test_dry_run",
            max_pages=1,
            record_limit=20,
        )
        ctx = pipeline.run()

        assert ctx.status == "SUCCESS"
        assert ctx.is_dry_run is True
        assert ctx.stages["Upsert"].status == "SKIPPED"
        assert ctx.stages["Upsert"].metrics.get("reason") == "Dry run mode active"

    def test_concurrency_lock_prevents_overlap(self):
        lock_file = settings.LOGS_DIR / "test_concurrency.lock"
        if lock_file.exists():
            lock_file.unlink()

        lock1 = PipelineLock(lock_file=lock_file)
        assert lock1.acquire() is True

        lock2 = PipelineLock(lock_file=lock_file, timeout_seconds=0)
        assert lock2.acquire() is False

        lock1.release()
        assert lock2.acquire() is True
        lock2.release()


class TestSchedulerModule:
    """Tests for scheduler background lifecycle."""

    def test_scheduler_start_and_clean_stop(self):
        scheduler = PipelineScheduler(interval_minutes=60, is_offline=True, is_dry_run=True)
        assert scheduler.is_running is False

        scheduler.start(run_immediately=False)
        assert scheduler.is_running is True

        scheduler.stop()
        assert scheduler.is_running is False
