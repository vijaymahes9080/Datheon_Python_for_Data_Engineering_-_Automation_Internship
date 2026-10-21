"""Database connection factory, connection pooling, and schema initialization."""

from __future__ import annotations

import logging
from contextlib import contextmanager
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from config.settings import settings
from src.persistence.models import Base

logger = logging.getLogger("streamforge.persistence.connection")

_global_engine: Engine | None = None
_global_session_factory: sessionmaker[Session] | None = None


def get_engine(db_url: str | None = None, echo: bool = False) -> Engine:
    """Create or return cached SQLAlchemy engine with optimized connection pooling."""
    global _global_engine, _global_session_factory
    url = db_url or settings.get_database_url()

    if _global_engine is None or db_url is not None:
        is_sqlite = url.startswith("sqlite")

        if is_sqlite:
            # SQLite does not support standard server pool sizing; use connect_args for multithreading
            engine = create_engine(
                url,
                echo=echo,
                connect_args={"check_same_thread": False, "timeout": 30},
            )
        else:
            # PostgreSQL connection pool parameters as per optimization guidelines
            engine = create_engine(
                url,
                echo=echo,
                pool_size=10,
                max_overflow=20,
                pool_timeout=30,
                pool_pre_ping=True,
            )

        if db_url is None:
            _global_engine = engine
            _global_session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
            return _global_engine
        return engine

    return _global_engine


def get_session_factory(engine: Engine | None = None) -> sessionmaker[Session]:
    """Get or create configured sessionmaker factory."""
    global _global_session_factory
    eng = engine or get_engine()
    if _global_session_factory is None or engine is not None:
        factory = sessionmaker(bind=eng, autoflush=False, autocommit=False)
        if engine is None:
            _global_session_factory = factory
        return factory
    return _global_session_factory


@contextmanager
def get_session(engine: Engine | None = None) -> Generator[Session, None, None]:
    """Provide a transactional scope around a series of database operations."""
    factory = get_session_factory(engine)
    session: Session = factory()
    try:
        yield session
        session.commit()
    except Exception as exc:
        session.rollback()
        logger.error(f"Transaction rolled back due to error: {exc}")
        raise
    finally:
        session.close()


def init_database_schema(engine: Engine | None = None) -> None:
    """Initialize all database tables and indexes automatically."""
    eng = engine or get_engine()
    logger.info(f"Initializing database schema on {eng.url.render_as_string(hide_password=True)}...")
    Base.metadata.create_all(bind=eng)
    logger.info("Database schema initialized successfully.")
