from sqlalchemy.orm import Session

from tests.assertions import cli_output
from tests.factories.database import KindFactory, ProjectFactory
from tests.fixtures.cli import RunCli
from tests.fixtures.reporting_config import ReportingConfigFixture
from tests.fixtures.tracking_file import TrackingFileFixture

_PRINT_REPORTS_LIMIT = 10


def test_parse_fails_with_the_reason_for_an_unknown_alias(
    reporting_config: ReportingConfigFixture,
    run_cli: RunCli,
    tracking_file: TrackingFileFixture,
) -> None:
    reporting_config({"app": {"hour-report-path": str(tracking_file(["20.08.2026", "09 00 - a task - dev - mp"]))}})

    failure = run_cli("parse", "0")

    assert failure.exit_code == 1
    assert failure.out == ""
    assert cli_output.lines(failure.err) == [
        "Error",
        'Kind dev does not exist. Add it: reporting kind add dev "<name>"',
    ]


def test_parse_prints_only_the_count_when_there_are_ten_or_more_reports(
    reporting_config: ReportingConfigFixture,
    run_cli: RunCli,
    tracking_file: TrackingFileFixture,
) -> None:
    KindFactory.create(alias="dev", name="Develop")
    ProjectFactory.create(alias="mp", name="My Project")
    lines = _tracking_lines_for_days(_PRINT_REPORTS_LIMIT)
    reporting_config({"app": {"hour-report-path": str(tracking_file(lines)), "timezone": "UTC"}})

    result = run_cli("parse", "0")

    assert cli_output.lines(result.out) == [f"Parsed {_PRINT_REPORTS_LIMIT}"]


def test_parse_prints_the_report_it_imported(
    reporting_config: ReportingConfigFixture,
    run_cli: RunCli,
    tracking_file: TrackingFileFixture,
) -> None:
    KindFactory.create(alias="dev", name="Develop")
    ProjectFactory.create(alias="mp", name="My Project")
    reporting_config(
        {
            "app": {
                "hour-report-path": str(
                    tracking_file(["20.08.2026", "09 00 - alpha task - dev - mp", "10 30 - beta task - dev - mp"])
                ),
                "timezone": "UTC",
            },
        }
    )

    result = run_cli("parse", "0")

    rendered = cli_output.lines(result.out)
    assert rendered[0] == "Parsed 1"
    assert "Report 20.08.2026" in rendered
    assert "01:30  alpha task  My Project" in rendered


def test_parse_reports_nothing_for_an_empty_file(
    database_session: Session,
    reporting_config: ReportingConfigFixture,
    run_cli: RunCli,
    tracking_file: TrackingFileFixture,
) -> None:
    reporting_config({"app": {"hour-report-path": str(tracking_file())}})

    result = run_cli("parse")

    assert result.out == "Parsed 0\n"


def _tracking_lines_for_days(days: int) -> list[str]:
    lines: list[str] = []

    for day in range(1, days + 1):
        lines += [f"{day:02d}.08.2026", "09 00 - a task - dev - mp", "", ""]

    return lines
