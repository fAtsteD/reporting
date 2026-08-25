import contextlib
from collections.abc import Generator
from os import path

import sqlalchemy as sa
from sqlalchemy import event
from sqlalchemy.orm import Session, sessionmaker

from reporting import config
from reporting.database.exceptions import DatabaseNotConfiguredError

engine: sa.engine.Engine | None = None
session_factory: sessionmaker[Session] | None = None


def database_url() -> str:
    if not config.app.sqlite_database_path:
        raise DatabaseNotConfiguredError("Path to the database file is not configured")

    return "sqlite:///" + path.normpath(path.expanduser(config.app.sqlite_database_path))


def reconnect() -> None:
    """
    Recreate connection with session factory. Run migrations
    """
    global engine, session_factory

    url = database_url()

    if engine is not None:
        engine.dispose()

    engine = sa.create_engine(url)

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
        raise RuntimeError("Database connection is not initialized")

    alembic_cfg = Config()
    alembic_cfg.set_main_option("script_location", "reporting.database:migrations")
    alembic_cfg.set_main_option("sqlalchemy.url", str(engine.url))

    with engine.connect() as connection:
        alembic_cfg.attributes["connection"] = connection
        command.upgrade(alembic_cfg, "head")


@contextlib.contextmanager
def session_scope() -> Generator[Session]:
    if session_factory is None:
        reconnect()

    current_factory = session_factory

    if current_factory is None:
        raise RuntimeError("Database connection is not initialized")

    session = current_factory()

    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
