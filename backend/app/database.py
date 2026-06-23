"""SQLAlchemy engine + session. Portable across SQLite and Postgres (Neon/Render)."""
from sqlalchemy import create_engine, inspect, text
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


def apply_schema_patches() -> None:
    """Lightweight column adds for existing DBs (create_all does not alter tables)."""
    inspector = inspect(engine)
    tables = set(inspector.get_table_names())

    def add_column(table: str, column: str, sqlite_ddl: str, pg_ddl: str) -> None:
        if table not in tables:
            return
        columns = {c["name"] for c in inspector.get_columns(table)}
        if column in columns:
            return
        with engine.begin() as conn:
            conn.execute(text(sqlite_ddl if _is_sqlite else pg_ddl))

    add_column(
        "quiz_attempts",
        "mode",
        "ALTER TABLE quiz_attempts ADD COLUMN mode VARCHAR(20) NOT NULL DEFAULT 'final'",
        "ALTER TABLE quiz_attempts ADD COLUMN IF NOT EXISTS mode VARCHAR(20) NOT NULL DEFAULT 'final'",
    )
    add_column(
        "quiz_attempts",
        "report",
        "ALTER TABLE quiz_attempts ADD COLUMN report JSON",
        "ALTER TABLE quiz_attempts ADD COLUMN IF NOT EXISTS report JSONB",
    )
    add_column(
        "assessments",
        "report",
        "ALTER TABLE assessments ADD COLUMN report JSON",
        "ALTER TABLE assessments ADD COLUMN IF NOT EXISTS report JSONB",
    )


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def release_db_transaction(db) -> None:
    """Commit before slow external calls so Neon does not idle-in-transaction timeout."""
    if db.in_transaction():
        db.commit()
