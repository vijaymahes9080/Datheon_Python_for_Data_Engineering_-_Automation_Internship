"""Complete end-to-end ETL pipeline state machine with dry-run support."""

from __future__ import annotations

import datetime
import json
import logging
from pathlib import Path
from typing import Any
import pandas as pd
from sqlalchemy import select

from config.settings import settings
from src.extraction.scraper import StreamForgeScraper
from src.notifications.notifier import AlertService
from src.orchestration.context import PipelineContext
from src.persistence.analytics import DatabaseAnalytics
from src.persistence.connection import get_engine, get_session, init_database_schema
from src.persistence.models import PipelineExecution
from src.persistence.repository import JobRepository
from src.quality.cleaner import DataCleaner
from src.quality.profiler import QualityProfiler
from src.quality.validator import SchemaValidator

logger = logging.getLogger("streamforge.orchestration.pipeline")


class ETLPipeline:
    """End-to-end orchestrator executing:

    Extract -> Inspect -> Transform -> Validate -> Upsert -> Verify -> Report -> Notify.
    """

    def __init__(
        self,
        is_offline: bool = True,
        is_dry_run: bool = False,
        trigger_type: str = "manual",
        max_pages: int = 5,
        record_limit: int = 200,
    ):
        self.is_offline = is_offline
        self.is_dry_run = is_dry_run
        self.trigger_type = trigger_type
        self.max_pages = max_pages
        self.record_limit = record_limit

        self.engine = get_engine()
        self.repository = JobRepository(engine=self.engine)
        self.analytics = DatabaseAnalytics(engine=self.engine)
        self.notifier = AlertService()

    def run(self) -> PipelineContext:
        """Execute the full 8-stage ETL pipeline sequentially."""
        ctx = PipelineContext(trigger_type=self.trigger_type, is_dry_run=self.is_dry_run)
        logger.info(
            f"Starting pipeline execution {ctx.execution_id} "
            f"(trigger={self.trigger_type}, dry_run={self.is_dry_run}, offline={self.is_offline})"
        )

        try:
            # Stage 1: Extract
            self._stage_extract(ctx)

            # Stage 2: Inspect
            raw_profile = self._stage_inspect(ctx)

            # Stage 3: Transform
            transformed_df, cleaning_meta = self._stage_transform(ctx)

            # Stage 4: Validate
            valid_df = self._stage_validate(ctx, transformed_df)

            # Stage 5: Upsert (Skipped if dry-run)
            self._stage_upsert(ctx, valid_df)

            # Stage 6: Verify
            self._stage_verify(ctx)

            # Stage 7: Report
            self._stage_report(ctx, raw_profile, valid_df, cleaning_meta)

            # Pipeline execution succeeded
            ctx.finish(status="SUCCESS")

        except Exception as exc:
            logger.error(f"Pipeline execution halted due to error: {exc}", exc_info=True)
            ctx.finish(status="FAILED", error=str(exc))

        finally:
            # Stage 8: Notify (Always runs, alerting success or failure)
            self._stage_notify(ctx)

            # Persist execution run history
            self._persist_execution(ctx)

        return ctx

    def _stage_extract(self, ctx: PipelineContext) -> None:
        st = ctx.stages["Extract"]
        st.start()
        try:
            scraper = StreamForgeScraper(
                max_pages=self.max_pages,
                record_limit=self.record_limit,
                is_offline=self.is_offline,
            )
            records, report = scraper.run()
            ctx.raw_records = records
            st.complete({
                "pages_visited": len(report.pages_visited),
                "extracted_count": len(records),
                "duplicates_removed": report.duplicates_removed,
            })
        except Exception as exc:
            st.fail(str(exc))
            raise

    def _stage_inspect(self, ctx: PipelineContext) -> dict[str, Any]:
        st = ctx.stages["Inspect"]
        st.start()
        try:
            df = pd.DataFrame(ctx.raw_records)
            profile = QualityProfiler.profile_dataframe(df)
            st.complete({"columns": list(df.columns), "initial_records": len(df)})
            return profile
        except Exception as exc:
            st.fail(str(exc))
            raise

    def _stage_transform(self, ctx: PipelineContext) -> tuple[pd.DataFrame, dict[str, Any]]:
        st = ctx.stages["Transform"]
        st.start()
        try:
            raw_df = pd.DataFrame(ctx.raw_records)
            cleaned_df, meta = DataCleaner.clean(raw_df)
            st.complete({"renamed_columns_count": len(meta.get("renamed_columns", {}))})
            return cleaned_df, meta
        except Exception as exc:
            st.fail(str(exc))
            raise

    def _stage_validate(self, ctx: PipelineContext, df: pd.DataFrame) -> pd.DataFrame:
        st = ctx.stages["Validate"]
        st.start()
        try:
            valid_df, rejections, summary = SchemaValidator.validate_dataset(df, deduplicate=True)
            ctx.cleaned_records = valid_df.to_dict(orient="records") if not valid_df.empty else []
            ctx.rejected_records = rejections
            st.complete({
                "valid_count": len(ctx.cleaned_records),
                "rejected_count": len(rejections),
                "acceptance_rate": summary.get("acceptance_rate_pct"),
            })
            return valid_df
        except Exception as exc:
            st.fail(str(exc))
            raise

    def _stage_upsert(self, ctx: PipelineContext, df: pd.DataFrame) -> None:
        st = ctx.stages["Upsert"]
        if self.is_dry_run:
            logger.info("Dry-run mode enabled: Skipping database persistence.")
            st.skip(reason="Dry run mode active")
            return

        st.start()
        try:
            init_database_schema(self.engine)
            report = self.repository.upsert_records(ctx.cleaned_records)
            ctx.ingestion_metrics = report.to_dict()
            st.complete({
                "inserted": report.inserted,
                "updated": report.updated,
                "failed": report.failed,
            })
        except Exception as exc:
            st.fail(str(exc))
            raise

    def _stage_verify(self, ctx: PipelineContext) -> None:
        st = ctx.stages["Verify"]
        st.start()
        try:
            verification = self.analytics.generate_verification_report()
            ctx.verification_metrics = verification
            st.complete({
                "total_stored_in_db": verification.get("total_records"),
                "duplicates_in_db": verification.get("duplicate_count"),
                "audit_passed": verification.get("duplicate_audit_passed"),
            })
        except Exception as exc:
            st.fail(str(exc))
            raise

    def _stage_report(
        self,
        ctx: PipelineContext,
        raw_profile: dict[str, Any],
        cleaned_df: pd.DataFrame,
        cleaning_meta: dict[str, Any],
    ) -> None:
        st = ctx.stages["Report"]
        st.start()
        try:
            raw_df = pd.DataFrame(ctx.raw_records)
            val_summary = {
                "duplicates_removed": len(ctx.raw_records) - len(ctx.cleaned_records) - len(ctx.rejected_records),
                "acceptance_rate_pct": round(
                    (len(ctx.cleaned_records) / len(ctx.raw_records) * 100) if ctx.raw_records else 0, 2
                ),
            }
            QualityProfiler.generate_comparison_report(
                raw_df=raw_df,
                cleaned_df=cleaned_df,
                rejected_records=ctx.rejected_records,
                validation_summary=val_summary,
                cleaning_metadata=cleaning_meta,
            )
            st.complete({"reports_written": ["validation_report.json", "validation_summary.md"]})
        except Exception as exc:
            st.fail(str(exc))
            raise

    def _stage_notify(self, ctx: PipelineContext) -> None:
        st = ctx.stages["Notify"]
        st.start()
        try:
            self.notifier.notify(ctx)
            st.complete({"notification_dispatched": True})
        except Exception as exc:
            logger.warning(f"Notification dispatch failed: {exc}")
            st.complete({"notification_dispatched": False, "error": str(exc)})

    def _persist_execution(self, ctx: PipelineContext) -> None:
        """Record execution outcomes to persistent SQLite table and JSON run history."""
        try:
            init_database_schema(self.engine)
            with get_session(self.engine) as session:
                rec = PipelineExecution(
                    execution_id=ctx.execution_id,
                    trigger_type=ctx.trigger_type,
                    is_dry_run=ctx.is_dry_run,
                    status=ctx.status,
                    start_time=datetime.datetime.fromisoformat(ctx.start_time),
                    end_time=datetime.datetime.fromisoformat(ctx.end_time) if ctx.end_time else None,
                    duration_seconds=ctx.duration_seconds,
                    records_extracted=len(ctx.raw_records),
                    records_cleaned=len(ctx.cleaned_records),
                    records_inserted=ctx.ingestion_metrics.get("inserted", 0),
                    records_updated=ctx.ingestion_metrics.get("updated", 0),
                    records_rejected=len(ctx.rejected_records),
                    error_message=ctx.error_message,
                )
                session.add(rec)

            # Update reports/execution_history.json
            history_file = settings.REPORTS_DIR / "execution_history.json"
            history_list: list[dict[str, Any]] = []
            if history_file.exists():
                try:
                    history_list = json.loads(history_file.read_text(encoding="utf-8"))
                except Exception:
                    history_list = []

            history_list.insert(0, ctx.to_dict())
            # Keep latest 100 executions
            history_list = history_list[:100]
            history_file.write_text(json.dumps(history_list, indent=2), encoding="utf-8")

            logger.info(f"Execution {ctx.execution_id} persisted to database and history log.")

        except Exception as exc:
            logger.error(f"Failed to persist execution {ctx.execution_id}: {exc}")
