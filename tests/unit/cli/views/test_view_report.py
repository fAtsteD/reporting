import datetime

from reporting.cli.views import view_report
from reporting.database.models import Report
from tests.assertions import cli_output
from tests.factories.database import KindFactory, ProjectFactory, ReportFactory, TaskFactory
from tests.fixtures.reporting_config import ReportingConfigFixture

_CURRENT_DATE = datetime.date(2026, 9, 1)
_REPORT_DATE = datetime.date(2026, 8, 20)


def test_groups_tasks_under_their_kind_name(reporting_config: ReportingConfigFixture) -> None:
    report = _build_report(
        [
            ("Zeta", "beta task", 60 * 60),
            ("Zeta", "alpha task", 30 * 60),
            ("Alpha", "gamma task", 9 * 60 * 60 + 5 * 60),
        ]
    )

    output = cli_output.render(view_report.render(report, _CURRENT_DATE))

    cli_output.assert_lines(
        output,
        [
            "Report 20.08.2026",
            "Alpha",
            "09:05 gamma task My Project",
            "Zeta",
            "00:30 alpha task My Project",
            "01:00 beta task My Project",
            "total 10:35 · today 01.09.2026",
        ],
    )


def test_merges_two_kinds_with_the_same_name_into_one_group(reporting_config: ReportingConfigFixture) -> None:
    report = _build_report(
        [
            ("Develop", "first task", 60 * 60),
            ("Analysis", "second task", 60 * 60),
            ("Develop", "third task", 60 * 60),
        ]
    )

    output = cli_output.render(view_report.render(report, _CURRENT_DATE))

    cli_output.assert_lines(
        output,
        [
            "Report 20.08.2026",
            "Analysis",
            "01:00 second task My Project",
            "Develop",
            "01:00 first task My Project",
            "01:00 third task My Project",
            "total 03:00 · today 01.09.2026",
        ],
    )


def test_renders_a_note_when_the_report_has_no_tasks(reporting_config: ReportingConfigFixture) -> None:
    output = cli_output.render(view_report.render(ReportFactory.build(date=_REPORT_DATE), _CURRENT_DATE))

    cli_output.assert_lines(
        output,
        ["Report 20.08.2026", "Report does not have tasks", "total 00:00 · today 01.09.2026"],
    )


def test_shows_the_total_and_the_current_date_in_the_subtitle(reporting_config: ReportingConfigFixture) -> None:
    report = _build_report([("Develop", "only task", 90 * 60)])

    output = cli_output.render(view_report.render(report, _CURRENT_DATE))

    assert "total 01:30 · today 01.09.2026" in cli_output.lines(output)


def _build_report(tasks: list[tuple[str, str, int]]) -> Report:
    report = ReportFactory.build(date=_REPORT_DATE)
    project = ProjectFactory.build(name="My Project")

    for kind_name, summary, logged_seconds in tasks:
        TaskFactory.build(
            kind=KindFactory.build(name=kind_name),
            logged_seconds=logged_seconds,
            project=project,
            report=report,
            summary=summary,
        )

    return report
