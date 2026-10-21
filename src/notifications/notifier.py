"""Multi-channel alerting service supporting Console, SMTP, and Webhook notifications."""

from __future__ import annotations

import json
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any
import requests

from config.settings import settings
from src.orchestration.context import PipelineContext

logger = logging.getLogger("streamforge.notifications.notifier")


class AlertService:
    """Dispatches pipeline status alerts via Console, Email, and Webhook."""

    def __init__(self):
        self.console_enabled = settings.ALERT_CONSOLE_ENABLED
        self.smtp_enabled = settings.ALERT_SMTP_ENABLED
        self.webhook_enabled = settings.ALERT_WEBHOOK_ENABLED

    def notify(self, ctx: PipelineContext) -> None:
        """Dispatch notifications across all enabled channels."""
        title = f"[{settings.APP_NAME}] Pipeline Execution {ctx.status} - ID: {ctx.execution_id[:8]}"
        body = self._build_summary_message(ctx)

        # 1. Console Notification (Default fallback)
        if self.console_enabled:
            self._notify_console(title, body, ctx.status)

        # 2. Webhook Notification (Slack/Discord/Teams compatible)
        if self.webhook_enabled and settings.WEBHOOK_URL:
            self._notify_webhook(title, body, ctx)

        # 3. SMTP Email Notification
        if self.smtp_enabled and settings.SMTP_USER and settings.ALERT_EMAIL_RECIPIENT:
            self._notify_smtp(title, body)

    def _build_summary_message(self, ctx: PipelineContext) -> str:
        counts = ctx.to_dict()["record_counts"]
        dry_str = " (DRY RUN)" if ctx.is_dry_run else ""
        msg = [
            f"StreamForge Pipeline Status: {ctx.status}{dry_str}",
            f"Execution ID: {ctx.execution_id}",
            f"Trigger Type: {ctx.trigger_type}",
            f"Duration:     {ctx.duration_seconds}s",
            f"Extracted:    {counts['extracted']}",
            f"Cleaned:      {counts['cleaned']}",
            f"Inserted:     {counts['inserted']}",
            f"Updated:      {counts['updated']}",
            f"Rejected:     {counts['rejected']}",
        ]
        if ctx.error_message:
            msg.append(f"Error Details: {ctx.error_message}")

        return "\n".join(msg)

    def _notify_console(self, title: str, body: str, status: str) -> None:
        prefix = "[ALERT SUCCESS]" if status == "SUCCESS" else "[ALERT FAILURE]"
        print("\n" + "=" * 60)
        print(f" {prefix} {title}")
        print("=" * 60)
        print(body)
        print("=" * 60 + "\n")
        logger.info(f"Console alert dispatched for {title}")

    def _notify_webhook(self, title: str, body: str, ctx: PipelineContext) -> None:
        try:
            payload = {
                "text": f"*{title}*\n```{body}```",
                "execution_id": ctx.execution_id,
                "status": ctx.status,
            }
            # Mask URL in logs
            resp = requests.post(settings.WEBHOOK_URL, json=payload, timeout=5)
            logger.info(f"Webhook alert dispatched (status={resp.status_code})")
        except Exception as exc:
            logger.error(f"Failed to dispatch webhook alert: {exc}")

    def _notify_smtp(self, title: str, body: str) -> None:
        try:
            msg = MIMEMultipart()
            msg["From"] = settings.SMTP_USER
            msg["To"] = settings.ALERT_EMAIL_RECIPIENT
            msg["Subject"] = title
            msg.attach(MIMEText(body, "plain"))

            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)
            logger.info(f"SMTP alert emailed to {settings.ALERT_EMAIL_RECIPIENT}")
        except Exception as exc:
            logger.error(f"Failed to dispatch SMTP email: {exc}")
