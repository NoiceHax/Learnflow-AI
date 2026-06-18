"""SQLAlchemy engine + session. Portable across SQLite and Postgres (Neon/Render)."""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from .config import settings

_db_url = settings.database_url_resolved
_is_sqlite = _db_url.startswith("sqlite")
connect_args = {"check_same_thread": False} if _is_sqlite else {}

engine_kwargs: dict = {
    "connect_args": connect_args,
    "pool_pre_ping": True,
    "future": True,
}
if not _is_sqlite:
    engine_kwargs["pool_recycle"] = 300

engine = create_engine(_db_url, **engine_kwargs)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
