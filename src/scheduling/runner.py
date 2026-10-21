"""Background scheduler runner using Python schedule and threading."""

from __future__ import annotations

import logging
import threading
import time
from typing import Callable
import schedule

from config.settings import settings
from src.orchestration.lock import PipelineLock, PipelineLockedException
from src.orchestration.pipeline import ETLPipeline

logger = logging.getLogger("streamforge.scheduling.runner")


class PipelineScheduler:
    """Manages scheduled periodic ETL pipeline executions with concurrency protection."""

    def __init__(
        self,
        interval_minutes: int | None = None,
        is_offline: bool = True,
        is_dry_run: bool = False,
    ):
        self.interval_minutes = interval_minutes or settings.PIPELINE_SCHEDULE_INTERVAL_MINUTES
        self.is_offline = is_offline
        self.is_dry_run = is_dry_run
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._scheduler = schedule.Scheduler()
        self.last_run_time: str | None = None
        self.total_scheduled_runs: int = 0

    def _job(self) -> None:
        """Scheduled job wrapper enforcing concurrency lock."""
        logger.info(f"Triggering scheduled ETL execution (interval={self.interval_minutes}m)...")
        try:
            with PipelineLock(timeout_seconds=0):
                pipeline = ETLPipeline(
                    is_offline=self.is_offline,
                    is_dry_run=self.is_dry_run,
                    trigger_type="scheduled",
                )
                ctx = pipeline.run()
                self.last_run_time = ctx.start_time
                self.total_scheduled_runs += 1
                logger.info(f"Scheduled run completed with status: {ctx.status}")
        except PipelineLockedException:
            logger.warning("Scheduled job skipped: another pipeline execution is currently active.")
        except Exception as exc:
            logger.error(f"Scheduled job execution failed: {exc}", exc_info=True)

    def start(self, run_immediately: bool = False) -> None:
        """Start scheduler in a background thread."""
        if self._thread and self._thread.is_alive():
            logger.warning("Scheduler is already running.")
            return

        self._stop_event.clear()
        self._scheduler.clear()

        # Register schedule
        self._scheduler.every(self.interval_minutes).minutes.do(self._job)
        logger.info(f"Scheduler configured: running every {self.interval_minutes} minutes.")

        if run_immediately:
            threading.Thread(target=self._job, daemon=True).start()

        def _worker():
            while not self._stop_event.is_set():
                self._scheduler.run_pending()
                time.sleep(1)

        self._thread = threading.Thread(target=_worker, daemon=True, name="StreamForge-Scheduler")
        self._thread.start()
        logger.info("Scheduler background thread started.")

    def stop(self) -> None:
        """Safely signal scheduler to stop and wait for thread to join."""
        if not self._thread or not self._thread.is_alive():
            logger.info("Scheduler is not currently running.")
            return

        logger.info("Stopping scheduler thread...")
        self._stop_event.set()
        self._thread.join(timeout=5)
        self._thread = None
        self._scheduler.clear()
        logger.info("Scheduler stopped cleanly.")

    @property
    def is_running(self) -> bool:
        """Return True if background scheduler thread is active."""
        return self._thread is not None and self._thread.is_alive()
