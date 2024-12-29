from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine("sqlite:///:memory:")
session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))


def reconnect(sqlite_path: str) -> None:
    """
    Recreate connection with session. Run migrations
    """
    global engine, session
    engine = create_engine("sqlite:///" + sqlite_path)
    session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

    # TODO: migrations
