from collections.abc import Generator

import pytest
from sqlalchemy.orm import Session

from reporting.database import db_connection
from reporting.database.models import Base
from tests.factories import database as db_factory
from tests.fixtures.reporting_config import ReportingConfigFixture


@pytest.fixture
def database_session(reporting_config: ReportingConfigFixture) -> Generator[Session]:
    db_connection.reconnect()

    if not db_connection.engine or not db_connection.session_factory:
        raise RuntimeError("Database is not connected")

    session = db_connection.session_factory()
    db_factory.db_session = session

    yield session

    db_factory.db_session = None
    session.rollback()
    Base.metadata.drop_all(bind=db_connection.engine)
    db_connection.engine.dispose()
