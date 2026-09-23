import pytest

from reporting.database import db_connection
from reporting.database.exceptions import DatabaseNotConfiguredError
from tests.fixtures.reporting_config import ReportingConfigFixture


def test_builds_a_sqlite_url_from_the_configured_path(reporting_config: ReportingConfigFixture) -> None:
    reporting_config({"app": {"sqlite-database-path": "/tmp/reporting.db"}})

    assert db_connection.database_url() == "sqlite:////tmp/reporting.db"


def test_fails_when_the_database_path_is_not_configured(reporting_config: ReportingConfigFixture) -> None:
    reporting_config({"app": {"sqlite-database-path": ""}})

    with pytest.raises(DatabaseNotConfiguredError, match="Path to the database file is not configured"):
        db_connection.database_url()
