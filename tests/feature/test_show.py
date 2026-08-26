import datetime

import pytest

from reporting.database.models import Kind, Project, Report
from tests import rendered_output
from tests.conftest import ReportingConfigFixture
from tests.factories import KindFactory, ProjectFactory, ReportFactory, TaskFactory
from tests.fixtures.cli import RunCli

REPORT_CONFIG: dict = {
    "app": {
        "minute-round-to": 0,
        "timezone": "UTC",
        "work-day-hours": 8.0,
    },
}


def create_kind(kind_id: int, name: str) -> Kind:
    return KindFactory.create(alias=f"k{kind_id}", id=kind_id, name=name, tasks=[])


def create_project() -> Project:
    return ProjectFactory.create(alias="mp", id=1, name="My Project", tasks=[])


def create_report(report_id: int, report_date: datetime.date) -> Report:
    return ReportFactory.create(date=report_date, id=report_id, tasks=[])


def create_task(task_id: int, kind: Kind, project: Project, report: Report, summary: str, logged_seconds: int) -> None:
    TaskFactory.create(
        id=task_id,
        kind=kind,
        kinds_id=kind.id,
        logged_seconds=logged_seconds,
        project=project,
        projects_id=project.id,
        report=report,
        reports_id=report.id,
        summary=summary,
    )


def current_date_text() -> str:
    return datetime.datetime.now(datetime.UTC).strftime("%d.%m.%Y")


def report_subtitle(total_clock: str) -> list[str]:
    return [f"total {total_clock} \u00b7 today {current_date_text()}"]


def report_title(report_date_text: str) -> list[str]:
    return [f"Report {report_date_text}"]


def test_show_by_date_selects_that_report(
    reporting_config: ReportingConfigFixture,
    run_cli: RunCli,
) -> None:
    reporting_config(REPORT_CONFIG)
    create_report(1, datetime.date(2026, 8, 18))
    create_report(2, datetime.date(2026, 8, 19))
    create_report(3, datetime.date(2026, 8, 20))

    result = run_cli("show", "19.08.2026")

    assert rendered_output.cells(result.out)[0] == report_title("19.08.2026")


def test_show_without_a_date_selects_the_latest_report(
    reporting_config: ReportingConfigFixture,
    run_cli: RunCli,
) -> None:
    reporting_config(REPORT_CONFIG)
    create_report(1, datetime.date(2026, 8, 18))
    create_report(2, datetime.date(2026, 8, 20))
    create_report(3, datetime.date(2026, 8, 19))

    result = run_cli("show")

    assert rendered_output.cells(result.out)[0] == report_title("20.08.2026")


def test_show_groups_tasks_by_kind_name_not_by_kind_id(
    reporting_config: ReportingConfigFixture,
    run_cli: RunCli,
) -> None:
    reporting_config(REPORT_CONFIG)
    project = create_project()
    report = create_report(1, datetime.date(2026, 8, 20))
    first_kind = create_kind(1, "Zeta")
    second_kind = create_kind(2, "Alpha")
    create_task(1, first_kind, project, report, "beta task", 60 * 60)
    create_task(2, first_kind, project, report, "alpha task", 30 * 60)
    create_task(3, second_kind, project, report, "gamma task", 9 * 60 * 60 + 5 * 60)

    result = run_cli("show", "20.08.2026")

    assert rendered_output.cells(result.out) == [
        report_title("20.08.2026"),
        ["Alpha"],
        ["09:05", "gamma task", "My Project"],
        ["Zeta"],
        ["00:30", "alpha task", "My Project"],
        ["01:00", "beta task", "My Project"],
        report_subtitle("10:35"),
    ]


def test_show_merges_two_kinds_with_the_same_name_into_one_group(
    reporting_config: ReportingConfigFixture,
    run_cli: RunCli,
) -> None:
    reporting_config(REPORT_CONFIG)
    project = create_project()
    report = create_report(1, datetime.date(2026, 8, 20))
    first_kind = create_kind(1, "Develop")
    second_kind = create_kind(2, "Analysis")
    third_kind = create_kind(3, "Develop")
    create_task(1, first_kind, project, report, "first task", 60 * 60)
    create_task(2, second_kind, project, report, "second task", 60 * 60)
    create_task(3, third_kind, project, report, "third task", 60 * 60)

    result = run_cli("show", "20.08.2026")

    assert rendered_output.cells(result.out) == [
        report_title("20.08.2026"),
        ["Analysis"],
        ["01:00", "second task", "My Project"],
        ["Develop"],
        ["01:00", "first task", "My Project"],
        ["01:00", "third task", "My Project"],
        report_subtitle("03:00"),
    ]


def test_show_renders_a_report_without_tasks(
    reporting_config: ReportingConfigFixture,
    run_cli: RunCli,
) -> None:
    reporting_config(REPORT_CONFIG)
    create_report(1, datetime.date(2026, 8, 20))

    result = run_cli("show", "20.08.2026")

    assert rendered_output.cells(result.out) == [
        report_title("20.08.2026"),
        ["Report does not have tasks"],
        report_subtitle("00:00"),
    ]


@pytest.mark.parametrize(
    "logged_seconds, expected_clock",
    [
        pytest.param(0, "00:00", id="zero"),
        pytest.param(3 * 60 * 60 + 30 * 60, "03:30", id="padded hours"),
        pytest.param(9 * 60 * 60 + 5 * 60, "09:05", id="padded hours and minutes"),
        pytest.param(10 * 60 * 60 + 5 * 60, "10:05", id="padded minutes"),
        pytest.param(100 * 60 * 60, "100:00", id="three digit hours"),
    ],
)
def test_show_pads_clock_values(
    expected_clock: str,
    logged_seconds: int,
    reporting_config: ReportingConfigFixture,
    run_cli: RunCli,
) -> None:
    reporting_config(REPORT_CONFIG)
    project = create_project()
    report = create_report(1, datetime.date(2026, 8, 20))
    kind = create_kind(1, "Develop")
    create_task(1, kind, project, report, "only task", logged_seconds)

    result = run_cli("show", "20.08.2026")

    assert rendered_output.cells(result.out) == [
        report_title("20.08.2026"),
        ["Develop"],
        [expected_clock, "only task", "My Project"],
        report_subtitle(expected_clock),
    ]


@pytest.mark.parametrize(
    "arguments",
    [
        pytest.param([], id="latest report"),
        pytest.param(["01.01.2015"], id="by date"),
    ],
)
def test_show_fails_when_the_report_does_not_exist(
    arguments: list[str],
    reporting_config: ReportingConfigFixture,
    run_cli: RunCli,
) -> None:
    reporting_config(REPORT_CONFIG)

    failure = run_cli("show", *arguments)

    assert failure.exit_code == 1
    assert failure.out == ""
    assert failure.err == "Report does not exist\n"


def test_show_rejects_a_date_that_is_not_a_date(run_cli: RunCli) -> None:
    failure = run_cli("show", "bogus")

    assert failure.exit_code == 2
    assert failure.out == ""
    assert '"bogus" is not a date (DD.MM.YYYY) or "last"' in failure.err


def test_show_renders_the_report_as_a_panel(
    reporting_config: ReportingConfigFixture,
    run_cli: RunCli,
) -> None:
    reporting_config(REPORT_CONFIG)
    project = create_project()
    report = create_report(1, datetime.date(2026, 8, 20))
    kind = create_kind(1, "Develop")
    create_task(1, kind, project, report, "only task", 60 * 60)

    result = run_cli("show", "20.08.2026")

    assert result.out == (
        "\u256d\u2500 Report 20.08.2026 \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u256e\n"
        "\u2502        Develop                   \u2502\n"
        "\u2502 01:00  only task  My Project     \u2502\n"
        f"\u2570\u2500 total 01:00 \u00b7 today {current_date_text()} \u2500\u256f\n"
    )
