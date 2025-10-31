"""Database session utilities for SQLAlchemy persistence."""
import os
from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./debate_sessions.db")

sqlite_kwargs = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=sqlite_kwargs)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


def initDb() -> None:
    """Create database tables for the debate session model."""
    from .debate import DebateSession  # noqa: F401  # ensure models imported

    Base.metadata.create_all(bind=engine)


@contextmanager
def sessionScope() -> Iterator[Session]:
    """Provide a transactional scope around a series of operations."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def getSession() -> Iterator[Session]:
    """Yield a database session for dependency-injected FastAPI routes."""
    with sessionScope() as session:
        yield session
