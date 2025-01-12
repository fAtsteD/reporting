from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


def reconnect(sqlite_path: str) -> None:
    """
    Recreate connection with session. Run migrations
    """
    global engine, session
    session.remove()
    engine.dispose()
    engine = create_engine("sqlite:///" + sqlite_path)
    session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

    run_migrations()


def run_migrations() -> None:
    global engine
    from alembic import command
    from alembic.config import Config

    alembic_cfg = Config()
    alembic_cfg.set_main_option("script_location", "reporting:migrations")
    alembic_cfg.set_main_option("sqlalchemy.url", str(engine.url))

    with engine.connect() as connection:
        alembic_cfg.attributes["connection"] = connection
        command.upgrade(alembic_cfg, "head")


engine = create_engine("sqlite:///:memory:")
session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
