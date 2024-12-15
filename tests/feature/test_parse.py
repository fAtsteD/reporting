import datetime
import pathlib
from typing import Protocol, TypeGuard

import faker
import pytest
from sqlalchemy.orm import Session

from reporting import cli
from reporting.models.kind import Kind
from reporting.models.project import Project
from reporting.models.report import Report
from reporting.models.task import Task
from tests.conftest import ReportingConfigFixture
from tests.factories import KindFactory, ProjectFactory, ReportFactory


class TrackingFileFixture(Protocol):
    def __call__(self, lines: list[str] = []) -> pathlib.Path: ...


@pytest.fixture
def generate_tracking_file(tmp_path: pathlib.Path) -> TrackingFileFixture:
    tracking_file = pathlib.Path(tmp_path, "tracking.txt")

    def generate(lines: list[str] = []) -> pathlib.Path:
        tracking_file.write_text("\n".join(lines))
        return tracking_file

    return generate


def test_parse_empty_file(
    capsys: pytest.CaptureFixture,
    database_session: Session,
    generate_tracking_file: TrackingFileFixture,
    reporting_config: ReportingConfigFixture,
) -> None:
    reporting_config(
        {
            "hour-report-path": str(generate_tracking_file()),
        }
    )
    output_expected = "Parsed 0\n"

    cli.main(["--parse"])
    output = capsys.readouterr()

    assert output.out == output_expected
    assert database_session.query(Report).count() == 0
    assert database_session.query(Task).count() == 0


def test_parse_last_report_with_remove_tasks(
    capsys: pytest.CaptureFixture,
    database_session: Session,
    faker: faker.Faker,
    generate_tracking_file: TrackingFileFixture,
    reporting_config: ReportingConfigFixture,
) -> None:
    report_date = faker.date_object()
    projects: list[Project] = [
        ProjectFactory.create(tasks=[]),
        ProjectFactory.create(tasks=[]),
    ]
    types: list[Kind] = [
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
            f"12 30 - l",
            f"12 45 - {summaries[2]} - {types[0].alias} - {projects[1].alias}",
            f"13 30 - break",
            f"14 00 - {summaries[0]} - {types[1].alias}",
            f"15 35 - {summaries[3]} - {types[2].alias} - {projects[1].alias}",
            f"",
            f"",
            faker.date_object().strftime("%d.%m.%Y"),
            f"08 00 - {summaries[0]} - {types[1].alias}",
            f"09 00 - l",
            f"10 00 - {summaries[1]} - {types[0].alias}",
        ]
    )
    reporting_config(
        {
            "default-type": types[0].alias,
            "default-project": projects[0].alias,
            "dictionary": {
                "task": {
                    "l": "lunch",
                },
            },
            "hour-report-path": str(tracking_file_path),
            "minute-round-to": 15,
            "omit-task": [
                "break",
                "lunch",
            ],
        }
    )
    ReportFactory.create(date=report_date)

    cli.main(["--parse"])

    output = capsys.readouterr()
    assert str(output.out).startswith("Parsed 1\n")
    assert database_session.query(Report).filter(Report.date == report_date).count() == 1
    assert database_session.query(Task).count() == len(summaries)

    database_tasks = list(
        filter(
            None,
            [
                database_session.query(Task).filter(Task.summary == summaries[0]).first(),
                database_session.query(Task).filter(Task.summary == summaries[1]).first(),
                database_session.query(Task).filter(Task.summary == summaries[2]).first(),
                database_session.query(Task).filter(Task.summary == summaries[3]).first(),
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
    capsys: pytest.CaptureFixture,
    database_session: Session,
    faker: faker.Faker,
    generate_tracking_file: TrackingFileFixture,
    reporting_config: ReportingConfigFixture,
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
    projects: list[Project] = [
        ProjectFactory.create(tasks=[]),
        ProjectFactory.create(tasks=[]),
    ]
    types: list[Kind] = [
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
            f"12 30 - l",
            f"12 45 - {summaries[2]} - {types[0].alias} - {projects[1].alias}",
            f"13 30 - break",
            f"14 00 - {summaries[0]} - {types[1].alias}",
            f"15 35 - {summaries[3]} - {types[2].alias} - {projects[1].alias}",
            f"",
            f"",
            report_dates[1].strftime("%d.%m.%Y"),
            f"08 00 - {summaries[0]} - {types[1].alias}",
            f"09 00 - {summaries[1]} - {types[2].alias} - {projects[1].alias}",
            f"12 30 - lunch",
            f"13 00 - {summaries[2]} - {types[0].alias}",
            f"13 30 - break",
            f"14 00 - {summaries[3]} - {types[0].alias}",
            f"14 50 - {summaries[1]} - {types[2].alias} - {projects[1].alias}",
            f"",
            f"",
            report_dates[2].strftime("%d.%m.%Y"),
            f"08 00 - {summaries[1]} - {types[1].alias}",
            f"09 00 - {summaries[2]} - {types[2].alias} - {projects[1].alias}",
            f"10 00 - {summaries[3]} - {types[0].alias} - {projects[1].alias}",
            f"12 30 - l",
            f"12 45 - {summaries[0]} - {types[1].alias} - {projects[0].alias}",
            f"13 30 - break",
            f"14 00 - {summaries[1]} - {types[1].alias}",
            f"15 35 - {summaries[3]} - {types[0].alias} - {projects[1].alias}",
            f"",
            f"",
            faker.date_object().strftime("%d.%m.%Y"),
            f"08 00 - {summaries[0]} - {types[1].alias}",
            f"10 00 - {summaries[1]} - {types[0].alias}",
            f"12 30 - l",
            f"12 45 - {summaries[2]} - {types[0].alias} - {projects[1].alias}",
            f"13 30 - break",
            f"14 00 - {summaries[0]} - {types[1].alias}",
            f"15 35 - {summaries[3]} - {types[2].alias} - {projects[1].alias}",
        ]
    )
    reporting_config(
        {
            "default-type": types[0].alias,
            "default-project": projects[0].alias,
            "dictionary": {
                "task": {
                    "l": "lunch",
                },
            },
            "hour-report-path": str(tracking_file_path),
            "minute-round-to": 15,
            "omit-task": [
                "break",
                "lunch",
            ],
        }
    )

    cli.main(["--parse", "3"])

    output = capsys.readouterr()
    assert str(output.out).startswith("Parsed 3\n")
    assert database_session.query(Report).count() == 3
    assert database_session.query(Task).count() == 12

    database_reports = list(
        filter(
            None,
            [
                database_session.query(Report).filter(Report.date == report_dates[0]).first(),
                database_session.query(Report).filter(Report.date == report_dates[1]).first(),
                database_session.query(Report).filter(Report.date == report_dates[2]).first(),
            ],
        )
    )
    database_reports_tasks = []

    for database_report in database_reports:
        database_reports_tasks += list(
            filter(
                None,
                [
                    database_session.query(Task)
                    .filter(
                        Task.summary == summaries[0],
                        Task.reports_id == database_report.id,
                    )
                    .first(),
                    database_session.query(Task)
                    .filter(
                        Task.summary == summaries[1],
                        Task.reports_id == database_report.id,
                    )
                    .first(),
                    database_session.query(Task)
                    .filter(
                        Task.summary == summaries[2],
                        Task.reports_id == database_report.id,
                    )
                    .first(),
                    database_session.query(Task)
                    .filter(
                        Task.summary == summaries[3],
                        Task.reports_id == database_report.id,
                    )
                    .first(),
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
