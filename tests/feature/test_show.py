import datetime

import faker
import pytest

from reporting import cli
from reporting.models.report import Report
from tests.conftest import ReportingConfigFixture
from tests.factories import ReportFactory


def test_show_by_date(
    capsys: pytest.CaptureFixture,
    reporting_config: ReportingConfigFixture,
) -> None:
    reporting_config()
    reports: list[Report] = ReportFactory.create_batch(size=10)
    reports.sort(key=lambda report: report.date)

    cli.main(["--show", reports[2].date.strftime("%d.%m.%Y")])

    output = capsys.readouterr()

    assert output.out == f"{reports[2]}\n"


@pytest.mark.parametrize(
    "is_report_exist",
    [
        pytest.param(
            False,
            id="no reports",
        ),
        pytest.param(
            True,
            id="some reports exists",
        ),
    ],
)
def test_show_last(
    capsys: pytest.CaptureFixture,
    is_report_exist: bool,
    reporting_config: ReportingConfigFixture,
) -> None:
    reporting_config()
    reports: list[Report] = []

    if is_report_exist:
        reports = ReportFactory.create_batch(size=3)

    reports.sort(key=lambda report: report.date, reverse=True)

    cli.main(["--show"])

    output = capsys.readouterr()

    if is_report_exist:
        assert output.out == f"{reports[0]}\n"
    else:
        assert output.out == "Report does not exist\n"


@pytest.mark.parametrize(
    "is_generate_report",
    [
        pytest.param(
            False,
            id="no reports",
        ),
        pytest.param(
            True,
            id="not exist report",
        ),
    ],
)
def test_show_not_exist(
    capsys: pytest.CaptureFixture,
    faker: faker.Faker,
    is_generate_report: bool,
    reporting_config: ReportingConfigFixture,
) -> None:
    reporting_config()

    if is_generate_report:
        ReportFactory.create(date=faker.date_object(datetime.datetime(2010, 1, 1)))
        ReportFactory.create(date=faker.date_object(datetime.datetime(2010, 1, 1)))

    cli.main(["--show", "01.01.2015"])

    output = capsys.readouterr()
    assert output.out == "Report does not exist\n"
