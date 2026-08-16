import contextlib
from collections.abc import Generator

import sqlalchemy as sa
from sqlalchemy import event
from sqlalchemy.orm import Session, sessionmaker

engine: sa.engine.Engine | None = None
session_factory: sessionmaker[Session] | None = None


def reconnect(sqlite_path: str) -> None:
    """
    Recreate connection with session factory. Run migrations
    """
    global engine, session_factory

    if engine is not None:
        engine.dispose()

    engine = sa.create_engine("sqlite:///" + sqlite_path)

    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, _) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    session_factory = sessionmaker(bind=engine, autoflush=False)

    run_migrations()


def run_migrations() -> None:
    from alembic import command
    from alembic.config import Config

    if engine is None:
        raise RuntimeError("Database is not connected. Call reconnect() first.")

    alembic_cfg = Config()
    alembic_cfg.set_main_option("script_location", "reporting.database:migrations")
    alembic_cfg.set_main_option("sqlalchemy.url", str(engine.url))

    with engine.connect() as connection:
        alembic_cfg.attributes["connection"] = connection
        command.upgrade(alembic_cfg, "head")


@contextlib.contextmanager
def session_scope() -> Generator[Session]:
    """
    Transactional scope: commit on success, rollback on error, always close
    """
    if session_factory is None:
        raise RuntimeError("Database is not connected. Call reconnect() first.")

    session = session_factory()

    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
