"""Pipeline execution context and stage state tracking."""

from __future__ import annotations

import datetime
import uuid
from typing import Any


class StageOutcome:
    """Status and duration of a single pipeline stage."""

    def __init__(self, name: str):
        self.name = name
        self.status = "PENDING"  # PENDING, RUNNING, SUCCESS, FAILED, SKIPPED
        self.start_time: str | None = None
        self.end_time: str | None = None
        self.duration_seconds: float = 0.0
        self.error_message: str | None = None
        self.metrics: dict[str, Any] = {}

    def start(self) -> None:
        self.status = "RUNNING"
        self.start_time = datetime.datetime.now(datetime.timezone.utc).isoformat()

    def complete(self, metrics: dict[str, Any] | None = None) -> None:
        self.status = "SUCCESS"
        self.end_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
        if self.start_time:
            t0 = datetime.datetime.fromisoformat(self.start_time)
            t1 = datetime.datetime.fromisoformat(self.end_time)
            self.duration_seconds = round((t1 - t0).total_seconds(), 3)
        self.metrics = metrics or {}

    def fail(self, error: str) -> None:
        self.status = "FAILED"
        self.end_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
        if self.start_time:
            t0 = datetime.datetime.fromisoformat(self.start_time)
            t1 = datetime.datetime.fromisoformat(self.end_time)
            self.duration_seconds = round((t1 - t0).total_seconds(), 3)
        self.error_message = error

    def skip(self, reason: str = "Dry run mode") -> None:
        self.status = "SKIPPED"
        self.metrics = {"reason": reason}

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "status": self.status,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_seconds": self.duration_seconds,
            "error_message": self.error_message,
            "metrics": self.metrics,
        }


class PipelineContext:
    """Stateful execution context across the 8 sequential pipeline stages."""

    STAGES = ["Extract", "Inspect", "Transform", "Validate", "Upsert", "Verify", "Report", "Notify"]

    def __init__(self, trigger_type: str = "manual", is_dry_run: bool = False):
        self.execution_id: str = str(uuid.uuid4())
        self.trigger_type: str = trigger_type
        self.is_dry_run: bool = is_dry_run
        self.status: str = "RUNNING"
        self.start_time: str = datetime.datetime.now(datetime.timezone.utc).isoformat()
        self.end_time: str | None = None
        self.duration_seconds: float = 0.0
        self.error_message: str | None = None

        self.stages: dict[str, StageOutcome] = {s: StageOutcome(s) for s in self.STAGES}

        # Shared data artifacts passed between stages
        self.raw_records: list[dict[str, Any]] = []
        self.cleaned_records: list[dict[str, Any]] = []
        self.rejected_records: list[dict[str, Any]] = []
        self.ingestion_metrics: dict[str, Any] = {}
        self.verification_metrics: dict[str, Any] = {}

    def finish(self, status: str = "SUCCESS", error: str | None = None) -> None:
        self.status = status
        self.error_message = error
        self.end_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
        t0 = datetime.datetime.fromisoformat(self.start_time)
        t1 = datetime.datetime.fromisoformat(self.end_time)
        self.duration_seconds = round((t1 - t0).total_seconds(), 3)

    def to_dict(self) -> dict[str, Any]:
        return {
            "execution_id": self.execution_id,
            "trigger_type": self.trigger_type,
            "is_dry_run": self.is_dry_run,
            "status": self.status,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_seconds": self.duration_seconds,
            "error_message": self.error_message,
            "stages": {name: stage.to_dict() for name, stage in self.stages.items()},
            "record_counts": {
                "extracted": len(self.raw_records),
                "cleaned": len(self.cleaned_records),
                "rejected": len(self.rejected_records),
                "inserted": self.ingestion_metrics.get("inserted", 0),
                "updated": self.ingestion_metrics.get("updated", 0),
            },
        }
