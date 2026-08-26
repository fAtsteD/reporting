import datetime
import pathlib
from typing import Protocol, TypeGuard

import faker
import pytest
import sqlalchemy as sa
from sqlalchemy.orm import Session

from reporting.database.models import Report, Task
from tests import rendered_output
from tests.conftest import ReportingConfigFixture
from tests.factories import KindFactory, ProjectFactory, ReportFactory
from tests.fixtures.cli import RunCli


class TrackingFileFixture(Protocol):
    def __call__(self, lines: list[str] | None = None) -> pathlib.Path: ...


@pytest.fixture
def generate_tracking_file(tmp_path: pathlib.Path) -> TrackingFileFixture:
    tracking_file = pathlib.Path(tmp_path, "tracking.txt")

    def generate(lines: list[str] | None = None) -> pathlib.Path:
        if lines is None:
            lines = []
        tracking_file.write_text("\n".join(lines))
        return tracking_file

    return generate


def test_parse_empty_file(
    database_session: Session,
    generate_tracking_file: TrackingFileFixture,
    reporting_config: ReportingConfigFixture,
    run_cli: RunCli,
) -> None:
    reporting_config(
        {
            "app": {
                "hour-report-path": str(generate_tracking_file()),
            },
        }
    )

    result = run_cli("parse")

    assert result.out == "Parsed 0\n"
    assert database_session.scalar(sa.select(sa.func.count()).select_from(Report)) == 0
    assert database_session.scalar(sa.select(sa.func.count()).select_from(Task)) == 0


def test_parse_last_report_with_remove_tasks(
    database_session: Session,
    faker: faker.Faker,
    generate_tracking_file: TrackingFileFixture,
    reporting_config: ReportingConfigFixture,
    run_cli: RunCli,
) -> None:
    report_date = faker.date_object()
    projects = [
        ProjectFactory.create(tasks=[]),
        ProjectFactory.create(tasks=[]),
    ]
    types = [
        KindFactory.create(tasks=[]),
        KindFactory.create(tasks=[]),
        KindFactory.create(tasks=[]),
    ]
    summaries = [
        faker.sentence(nb_words=10, variable_nb_words=True),
        faker.sentence(nb_words=10, variable_nb_words=True),
        faker.sentence(nb_words=10, variable_nb_words=True),
        faker.sentence(nb_words=10, variable_nb_words=True),
    ]
    tracking_file_path = generate_tracking_file(
        [
            report_date.strftime("%d.%m.%Y"),
            f"08 00 - {summaries[0]} - {types[1].alias}",
            f"10 00 - {summaries[1]} - {types[0].alias}",
            "12 30 - l",
            f"12 45 - {summaries[2]} - {types[0].alias} - {projects[1].alias}",
            "13 30 - break",
            f"14 00 - {summaries[0]} - {types[1].alias}",
            f"15 35 - {summaries[3]} - {types[2].alias} - {projects[1].alias}",
            "",
            "",
            faker.date_object().strftime("%d.%m.%Y"),
            f"08 00 - {summaries[0]} - {types[1].alias}",
            "09 00 - l",
            f"10 00 - {summaries[1]} - {types[0].alias}",
        ]
    )
    reporting_config(
        {
            "app": {
                "default-project": projects[0].alias,
                "default-type": types[0].alias,
                "hour-report-path": str(tracking_file_path),
                "minute-round-to": 15,
                "omit-task": [
                    "break",
                    "lunch",
                ],
            },
            "dictionary": {
                "task": {
                    "l": "lunch",
                },
            },
        }
    )
    ReportFactory.create(date=report_date)

    result = run_cli("parse")

    assert result.out.startswith("Parsed 1\n")
    assert (
        database_session.scalar(sa.select(sa.func.count()).select_from(Report).where(Report.date == report_date)) == 1
    )
    assert database_session.scalar(sa.select(sa.func.count()).select_from(Task)) == len(summaries)

    database_tasks = list(
        filter(
            None,
            [
                database_session.scalars(sa.select(Task).where(Task.summary == summaries[0])).first(),
                database_session.scalars(sa.select(Task).where(Task.summary == summaries[1])).first(),
                database_session.scalars(sa.select(Task).where(Task.summary == summaries[2])).first(),
                database_session.scalars(sa.select(Task).where(Task.summary == summaries[3])).first(),
            ],
        )
    )
    assert len(database_tasks) == len(summaries)
    assert database_tasks[0].logged_seconds == (3 * 60 + 35) * 60
    assert database_tasks[0].kinds_id == types[1].id
    assert database_tasks[0].projects_id == projects[0].id
    assert database_tasks[1].logged_seconds == (2 * 60 + 30) * 60
    assert database_tasks[1].kinds_id == types[0].id
    assert database_tasks[1].projects_id == projects[0].id
    assert database_tasks[2].logged_seconds == (45) * 60
    assert database_tasks[2].kinds_id == types[0].id
    assert database_tasks[2].projects_id == projects[1].id
    assert database_tasks[3].logged_seconds == (1 * 60 + 10) * 60
    assert database_tasks[3].kinds_id == types[2].id
    assert database_tasks[3].projects_id == projects[1].id


def test_parse_n_reports(
    database_session: Session,
    faker: faker.Faker,
    generate_tracking_file: TrackingFileFixture,
    reporting_config: ReportingConfigFixture,
    run_cli: RunCli,
) -> None:
    def filter_date(date) -> TypeGuard[datetime.date]:
        return isinstance(date, datetime.date)

    report_dates: list[datetime.date] = list(
        filter(
            filter_date,
            [
                faker.date_between(datetime.date(2000, 1, 1), datetime.date(2010, 1, 1)),
                faker.date_between(datetime.date(2010, 1, 2), datetime.date(2015, 1, 1)),
                faker.date_between(datetime.date(2015, 1, 2)),
            ],
        )
    )
    ReportFactory.create(date=report_dates[1])
    projects = [
        ProjectFactory.create(tasks=[]),
        ProjectFactory.create(tasks=[]),
    ]
    types = [
        KindFactory.create(tasks=[]),
        KindFactory.create(tasks=[]),
        KindFactory.create(tasks=[]),
    ]
    summaries = [
        faker.sentence(nb_words=10, variable_nb_words=True),
        faker.sentence(nb_words=10, variable_nb_words=True),
        faker.sentence(nb_words=10, variable_nb_words=True),
        faker.sentence(nb_words=10, variable_nb_words=True),
    ]
    tracking_file_path = generate_tracking_file(
        [
            report_dates[0].strftime("%d.%m.%Y"),
            f"08 00 - {summaries[0]} - {types[1].alias}",
            f"10 00 - {summaries[1]} - {types[0].alias}",
            "12 30 - l",
            f"12 45 - {summaries[2]} - {types[0].alias} - {projects[1].alias}",
            "13 30 - break",
            f"14 00 - {summaries[0]} - {types[1].alias}",
            f"15 35 - {summaries[3]} - {types[2].alias} - {projects[1].alias}",
            "",
            "",
            report_dates[1].strftime("%d.%m.%Y"),
            f"08 00 - {summaries[0]} - {types[1].alias}",
            f"09 00 - {summaries[1]} - {types[2].alias} - {projects[1].alias}",
            "12 30 - lunch",
            f"13 00 - {summaries[2]} - {types[0].alias}",
            "13 30 - break",
            f"14 00 - {summaries[3]} - {types[0].alias}",
            f"14 50 - {summaries[1]} - {types[2].alias} - {projects[1].alias}",
            "",
            "",
            report_dates[2].strftime("%d.%m.%Y"),
            f"08 00 - {summaries[1]} - {types[1].alias}",
            f"09 00 - {summaries[2]} - {types[2].alias} - {projects[1].alias}",
            f"10 00 - {summaries[3]} - {types[0].alias} - {projects[1].alias}",
            "12 30 - l",
            f"12 45 - {summaries[0]} - {types[1].alias} - {projects[0].alias}",
            "13 30 - break",
            f"14 00 - {summaries[1]} - {types[1].alias}",
            f"15 35 - {summaries[3]} - {types[0].alias} - {projects[1].alias}",
            "",
            "",
            faker.date_object().strftime("%d.%m.%Y"),
            f"08 00 - {summaries[0]} - {types[1].alias}",
            f"10 00 - {summaries[1]} - {types[0].alias}",
            "12 30 - l",
            f"12 45 - {summaries[2]} - {types[0].alias} - {projects[1].alias}",
            "13 30 - break",
            f"14 00 - {summaries[0]} - {types[1].alias}",
            f"15 35 - {summaries[3]} - {types[2].alias} - {projects[1].alias}",
        ]
    )
    reporting_config(
        {
            "app": {
                "default-project": projects[0].alias,
                "default-type": types[0].alias,
                "hour-report-path": str(tracking_file_path),
                "minute-round-to": 15,
                "omit-task": [
                    "break",
                    "lunch",
                ],
            },
            "dictionary": {
                "task": {
                    "l": "lunch",
                },
            },
        }
    )

    result = run_cli("parse", "3")

    assert result.out.startswith("Parsed 3\n")
    assert database_session.scalar(sa.select(sa.func.count()).select_from(Report)) == 3
    assert database_session.scalar(sa.select(sa.func.count()).select_from(Task)) == 12

    database_reports = list(
        filter(
            None,
            [
                database_session.scalars(sa.select(Report).where(Report.date == report_dates[0])).first(),
                database_session.scalars(sa.select(Report).where(Report.date == report_dates[1])).first(),
                database_session.scalars(sa.select(Report).where(Report.date == report_dates[2])).first(),
            ],
        )
    )
    database_reports_tasks = []

    for database_report in database_reports:
        database_reports_tasks += list(
            filter(
                None,
                [
                    database_session.scalars(
                        sa.select(Task).where(
                            Task.summary == summaries[0],
                            Task.reports_id == database_report.id,
                        )
                    ).first(),
                    database_session.scalars(
                        sa.select(Task).where(
                            Task.summary == summaries[1],
                            Task.reports_id == database_report.id,
                        )
                    ).first(),
                    database_session.scalars(
                        sa.select(Task).where(
                            Task.summary == summaries[2],
                            Task.reports_id == database_report.id,
                        )
                    ).first(),
                    database_session.scalars(
                        sa.select(Task).where(
                            Task.summary == summaries[3],
                            Task.reports_id == database_report.id,
                        )
                    ).first(),
                ],
            )
        )

    assert len(database_reports) == 3
    assert len(database_reports_tasks) == (len(summaries) * len(database_reports))

    assert database_reports_tasks[0].logged_seconds == (3 * 60 + 35) * 60
    assert database_reports_tasks[0].kinds_id == types[1].id
    assert database_reports_tasks[0].projects_id == projects[0].id
    assert database_reports_tasks[1].logged_seconds == (2 * 60 + 30) * 60
    assert database_reports_tasks[1].kinds_id == types[0].id
    assert database_reports_tasks[1].projects_id == projects[0].id
    assert database_reports_tasks[2].logged_seconds == (45) * 60
    assert database_reports_tasks[2].kinds_id == types[0].id
    assert database_reports_tasks[2].projects_id == projects[1].id
    assert database_reports_tasks[3].logged_seconds == (1 * 60 + 10) * 60
    assert database_reports_tasks[3].kinds_id == types[2].id
    assert database_reports_tasks[3].projects_id == projects[1].id

    assert database_reports_tasks[4].logged_seconds == (1 * 60) * 60
    assert database_reports_tasks[4].kinds_id == types[1].id
    assert database_reports_tasks[4].projects_id == projects[0].id
    assert database_reports_tasks[5].logged_seconds == (5 * 60 + 40) * 60
    assert database_reports_tasks[5].kinds_id == types[2].id
    assert database_reports_tasks[5].projects_id == projects[1].id
    assert database_reports_tasks[6].logged_seconds == (30) * 60
    assert database_reports_tasks[6].kinds_id == types[0].id
    assert database_reports_tasks[6].projects_id == projects[0].id
    assert database_reports_tasks[7].logged_seconds == (50) * 60
    assert database_reports_tasks[7].kinds_id == types[0].id
    assert database_reports_tasks[7].projects_id == projects[0].id

    assert database_reports_tasks[8].logged_seconds == (45) * 60
    assert database_reports_tasks[8].kinds_id == types[1].id
    assert database_reports_tasks[8].projects_id == projects[0].id
    assert database_reports_tasks[9].logged_seconds == (2 * 60 + 35) * 60
    assert database_reports_tasks[9].kinds_id == types[1].id
    assert database_reports_tasks[9].projects_id == projects[0].id
    assert database_reports_tasks[10].logged_seconds == (1 * 60) * 60
    assert database_reports_tasks[10].kinds_id == types[2].id
    assert database_reports_tasks[10].projects_id == projects[1].id
    assert database_reports_tasks[11].logged_seconds == (3 * 60 + 40) * 60
    assert database_reports_tasks[11].kinds_id == types[0].id
    assert database_reports_tasks[11].projects_id == projects[1].id


@pytest.mark.parametrize(
    "unknown_alias, expected_message",
    [
        pytest.param("dev", 'Kind dev does not exist. Add it: reporting kind add dev "<name>"', id="kind"),
        pytest.param("mp", 'Project mp does not exist. Add it: reporting project add mp "<name>"', id="project"),
    ],
)
def test_parse_fails_on_an_unknown_alias(
    database_session: Session,
    expected_message: str,
    generate_tracking_file: TrackingFileFixture,
    reporting_config: ReportingConfigFixture,
    run_cli: RunCli,
    unknown_alias: str,
) -> None:
    if unknown_alias != "dev":
        KindFactory.create(alias="dev", name="Develop", tasks=[])

    if unknown_alias != "mp":
        ProjectFactory.create(alias="mp", name="My Project", tasks=[])

    tracking_file_path = generate_tracking_file(
        [
            "20.08.2026",
            "09 00 - first task - dev - mp",
            "10 00 - second task - dev - mp",
        ]
    )
    reporting_config({"app": {"hour-report-path": str(tracking_file_path)}})

    failure = run_cli("parse", "0")

    assert failure.exit_code == 1
    assert failure.out == ""
    assert rendered_output.lines(failure.err) == ["Error", expected_message]
    assert database_session.scalar(sa.select(sa.func.count()).select_from(Task)) == 0


def test_parse_prints_every_report_when_fewer_than_ten(
    generate_tracking_file: TrackingFileFixture,
    reporting_config: ReportingConfigFixture,
    run_cli: RunCli,
) -> None:
    KindFactory.create(alias="dev", name="Develop", tasks=[])
    ProjectFactory.create(alias="mp", name="My Project", tasks=[])
    tracking_file_path = generate_tracking_file(
        [
            "20.08.2026",
            "09 00 - alpha task - dev - mp",
            "10 30 - beta task - dev - mp",
        ]
    )
    reporting_config(
        {
            "app": {
                "hour-report-path": str(tracking_file_path),
                "minute-round-to": 0,
                "timezone": "UTC",
                "work-day-hours": 8.0,
            },
        }
    )

    result = run_cli("parse", "0")
    current_date_text = datetime.datetime.now(datetime.UTC).strftime("%d.%m.%Y")

    assert rendered_output.cells(result.out) == [
        ["Parsed 1"],
        ["Report 20.08.2026"],
        ["Develop"],
        ["01:30", "alpha task", "My Project"],
        ["00:00", "beta task", "My Project"],
        [f"total 01:30 \u00b7 today {current_date_text}"],
    ]
