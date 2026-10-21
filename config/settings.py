"""StreamForge runtime configuration and settings."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Literal
from dotenv import load_dotenv

# Base directory for the streamforge_etl package
PACKAGE_ROOT = Path(__file__).resolve().parent.parent

# Load .env if present
load_dotenv(PACKAGE_ROOT / ".env")


class Settings:
    """Global configuration settings for StreamForge."""

    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    APP_NAME: str = os.getenv("APP_NAME", "StreamForge")

    # Storage Paths (resolved to absolute paths based on PACKAGE_ROOT)
    BASE_DIR: Path = PACKAGE_ROOT
    DATA_RAW_DIR: Path = PACKAGE_ROOT / os.getenv("DATA_RAW_DIR", "data/raw")
    DATA_PROCESSED_DIR: Path = PACKAGE_ROOT / os.getenv("DATA_PROCESSED_DIR", "data/processed")
    DATA_FIXTURES_DIR: Path = PACKAGE_ROOT / os.getenv("DATA_FIXTURES_DIR", "data/fixtures")
    HTML_FIXTURES_DIR: Path = DATA_FIXTURES_DIR / "html"
    REPORTS_DIR: Path = PACKAGE_ROOT / os.getenv("REPORTS_DIR", "reports")
    LOGS_DIR: Path = PACKAGE_ROOT / os.getenv("LOGS_DIR", "logs")
    DATABASE_DIR: Path = PACKAGE_ROOT / "database"

    # Database Settings
    DATABASE_DIALECT: Literal["sqlite", "postgresql"] = os.getenv("DATABASE_DIALECT", "sqlite").lower()  # type: ignore
    SQLITE_DB_PATH: Path = PACKAGE_ROOT / os.getenv("SQLITE_DB_PATH", "database/streamforge.db")
    
    # Optional PostgreSQL parameters
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", "5432"))
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "streamforge_db")
    POSTGRES_URL: str | None = os.getenv("POSTGRES_URL")

    # Scraper Settings
    SCRAPER_DEFAULT_DELAY_SEC: float = float(os.getenv("SCRAPER_DEFAULT_DELAY_SEC", "1.0"))
    SCRAPER_REQUEST_TIMEOUT_SEC: int = int(os.getenv("SCRAPER_REQUEST_TIMEOUT_SEC", "10"))
    SCRAPER_MAX_RETRIES: int = int(os.getenv("SCRAPER_MAX_RETRIES", "3"))
    SCRAPER_BACKOFF_FACTOR: float = float(os.getenv("SCRAPER_BACKOFF_FACTOR", "1.5"))
    SCRAPER_MAX_PAGES: int = int(os.getenv("SCRAPER_MAX_PAGES", "5"))
    SCRAPER_MAX_RECORDS: int = int(os.getenv("SCRAPER_MAX_RECORDS", "200"))
    SCRAPER_USER_AGENT: str = os.getenv(
        "SCRAPER_USER_AGENT",
        "StreamForge-DataExtractor/1.0 (+https://github.com/vijaymahes9080/Datheon_Python_for_Data_Engineering_-_Automation_Internship)",
    )

    # Alerts & Notifications
    ALERT_CONSOLE_ENABLED: bool = os.getenv("ALERT_CONSOLE_ENABLED", "true").lower() in ("true", "1", "yes")
    ALERT_SMTP_ENABLED: bool = os.getenv("ALERT_SMTP_ENABLED", "false").lower() in ("true", "1", "yes")
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    ALERT_EMAIL_RECIPIENT: str = os.getenv("ALERT_EMAIL_RECIPIENT", "")

    ALERT_WEBHOOK_ENABLED: bool = os.getenv("ALERT_WEBHOOK_ENABLED", "false").lower() in ("true", "1", "yes")
    WEBHOOK_URL: str = os.getenv("WEBHOOK_URL", "")

    # Scheduler
    PIPELINE_SCHEDULE_INTERVAL_MINUTES: int = int(os.getenv("PIPELINE_SCHEDULE_INTERVAL_MINUTES", "60"))
    PIPELINE_SCHEDULE_TIMEZONE: str = os.getenv("PIPELINE_SCHEDULE_TIMEZONE", "UTC")

    @classmethod
    def get_database_url(cls) -> str:
        """Return SQLAlchemy database connection string based on configured dialect."""
        if cls.DATABASE_DIALECT == "postgresql":
            if cls.POSTGRES_URL:
                return cls.POSTGRES_URL
            return f"postgresql+psycopg2://{cls.POSTGRES_USER}:{cls.POSTGRES_PASSWORD}@{cls.POSTGRES_HOST}:{cls.POSTGRES_PORT}/{cls.POSTGRES_DB}"
        
        # Default SQLite
        cls.SQLITE_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        return f"sqlite:///{cls.SQLITE_DB_PATH.as_posix()}"

    @classmethod
    def ensure_directories(cls) -> None:
        """Ensure all required runtime directories exist."""
        for path in [
            cls.DATA_RAW_DIR,
            cls.DATA_PROCESSED_DIR,
            cls.DATA_FIXTURES_DIR,
            cls.HTML_FIXTURES_DIR,
            cls.REPORTS_DIR,
            cls.LOGS_DIR,
            cls.DATABASE_DIR,
        ]:
            path.mkdir(parents=True, exist_ok=True)


settings = Settings()
settings.ensure_directories()
