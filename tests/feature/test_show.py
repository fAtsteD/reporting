import datetime

import pytest

from tests.assertions import cli_output
from tests.factories.database import KindFactory, ProjectFactory, ReportFactory, TaskFactory
from tests.fixtures.cli import RunCli


def test_show_exits_with_a_usage_error_for_a_bad_date(run_cli: RunCli) -> None:
    failure = run_cli("show", "bogus")

    assert failure.exit_code == 2
    assert failure.out == ""
    assert '"bogus" is not a date (DD.MM.YYYY) or "last"' in failure.err


@pytest.mark.parametrize(
    "arguments",
    [
        pytest.param([], id="the latest report"),
        pytest.param(["01.01.2015"], id="a report of a given date"),
    ],
)
def test_show_fails_when_the_report_does_not_exist(
    arguments: list[str],
    run_cli: RunCli,
) -> None:
    failure = run_cli("show", *arguments)

    assert failure.exit_code == 1
    assert failure.out == ""
    assert failure.err == "Report does not exist\n"


def test_show_prints_the_report_of_the_given_date(
    run_cli: RunCli,
) -> None:
    ReportFactory.create(date=datetime.date(2026, 8, 18))
    report = ReportFactory.create(date=datetime.date(2026, 8, 19))
    TaskFactory.create(
        kind=KindFactory.create(name="Develop"),
        logged_seconds=90 * 60,
        project=ProjectFactory.create(name="My Project"),
        report=report,
        summary="only task",
    )

    result = run_cli("show", "19.08.2026")

    assert cli_output.lines(result.out)[0] == "Report 19.08.2026"
    assert "01:30  only task  My Project" in cli_output.lines(result.out)


def test_show_without_a_date_prints_the_latest_report(
    run_cli: RunCli,
) -> None:
    ReportFactory.create(date=datetime.date(2026, 8, 18))
    ReportFactory.create(date=datetime.date(2026, 8, 20))
    ReportFactory.create(date=datetime.date(2026, 8, 19))

    result = run_cli("show")

    assert cli_output.lines(result.out)[0] == "Report 20.08.2026"
