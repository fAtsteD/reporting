import datetime
from zoneinfo import ZoneInfo

import pytest
from sqlalchemy.orm import Session

from reporting.database.models import Project

_KYIV_NOON = datetime.datetime(2026, 7, 1, 12, 0, tzinfo=ZoneInfo("Europe/Kyiv"))


@pytest.mark.parametrize(
    "stored, expected",
    [
        pytest.param(
            _KYIV_NOON,
            datetime.datetime(2026, 7, 1, 9, 0, tzinfo=datetime.UTC),
            id="an aware datetime is converted to utc",
        ),
        pytest.param(
            datetime.datetime(2026, 7, 1, 12, 0),  # noqa: DTZ001
            datetime.datetime(2026, 7, 1, 12, 0, tzinfo=datetime.UTC),
            id="a naive datetime is read as utc",
        ),
    ],
)
def test_reads_back_a_stored_datetime_as_utc(
    database_session: Session,
    expected: datetime.datetime,
    stored: datetime.datetime,
) -> None:
    project = Project(alias="project", created_at=stored, name="Project", updated_at=stored)
    database_session.add(project)
    database_session.commit()
    database_session.expire(project)

    assert project.created_at == expected
    assert project.updated_at == expected
