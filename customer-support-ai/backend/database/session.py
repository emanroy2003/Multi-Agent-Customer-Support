"""
Database session management (SQLAlchemy).

Supports Postgres (production) or SQLite (local dev) via
`DATABASE_TYPE` in .env. Mongo support can be added later by
swapping this module for a Motor-based one; the rest of the app
only depends on `get_db`.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from backend.config import settings

connect_args = {"check_same_thread": False} if settings.database_type == "sqlite" else {}

engine = create_engine(settings.database_url, connect_args=connect_args, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """FastAPI dependency that yields a DB session and always closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables. Called once on application startup."""
    # Import models here so they're registered on Base.metadata before create_all
    from backend.models import user, conversation  # noqa: F401

    Base.metadata.create_all(bind=engine)
