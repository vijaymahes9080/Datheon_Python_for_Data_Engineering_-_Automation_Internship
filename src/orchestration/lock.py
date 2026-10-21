"""File-based process concurrency locking preventing overlapping pipeline executions."""

from __future__ import annotations

import logging
import os
import time
from pathlib import Path

from config.settings import settings

logger = logging.getLogger("streamforge.orchestration.lock")


class PipelineLockedException(Exception):
    """Raised when an execution is attempted while another pipeline is currently running."""


class PipelineLock:
    """Exclusive file-based lock guaranteeing single-instance pipeline execution."""

    def __init__(self, lock_file: Path | None = None, timeout_seconds: float = 0.0):
        self.lock_file = lock_file or (settings.LOGS_DIR / "pipeline.lock")
        self.timeout_seconds = timeout_seconds
        self._acquired = False

    def acquire(self) -> bool:
        """Attempt to acquire exclusive file lock."""
        self.lock_file.parent.mkdir(parents=True, exist_ok=True)
        start_t = time.time()

        while True:
            try:
                # Use exclusive file creation flag 'x' (O_CREAT | O_EXCL)
                with open(self.lock_file, "x", encoding="utf-8") as f:
                    f.write(f"PID: {os.getpid()}\nTime: {time.time()}\n")
                self._acquired = True
                logger.info(f"Acquired pipeline lock at {self.lock_file}")
                return True
            except FileExistsError:
                if self.timeout_seconds <= 0 or (time.time() - start_t) > self.timeout_seconds:
                    logger.warning(f"Could not acquire pipeline lock; lock held at {self.lock_file}")
                    return False
                time.sleep(0.5)

    def release(self) -> None:
        """Release the file lock."""
        if self._acquired and self.lock_file.exists():
            try:
                self.lock_file.unlink()
                logger.info(f"Released pipeline lock at {self.lock_file}")
            except Exception as exc:
                logger.error(f"Failed to release pipeline lock: {exc}")
            finally:
                self._acquired = False

    def __enter__(self):
        if not self.acquire():
            raise PipelineLockedException(
                f"Another pipeline execution is currently in progress. Lock file: {self.lock_file}"
            )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()
