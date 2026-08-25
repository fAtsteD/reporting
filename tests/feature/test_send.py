import datetime

import pytest

from reporting.cli.commands.send import SEND_QUESTION
from reporting.database.models import Report
from reporting.services.jira import jira_service
from reporting.services.qatestlab_portal import qatestlab_portal_service
from reporting.services.report import report_service
from tests.conftest import ReportingConfigFixture
from tests.factories import ReportFactory
from tests.fixtures.cli import RunCli

REPORT_DATE = datetime.date(2026, 8, 20)


def current_date_text() -> str:
    return datetime.datetime.now(datetime.UTC).strftime("%d.%m.%Y")


def question_text() -> str:
    return f"Report date: 20.08.2026\nCurrent date: {current_date_text()}\n"


def test_send_asks_one_question_for_both_targets(
    monkeypatch: pytest.MonkeyPatch,
    reporting_config: ReportingConfigFixture,
    run_cli: RunCli,
) -> None:
    reporting_config({"app": {"timezone": "UTC"}})
    report = ReportFactory.create(date=REPORT_DATE, id=1, tasks=[])
    questions: list[str] = []
    sent_by: list[str] = []

    def answer(question: str) -> str:
        questions.append(question)
        return "y"

    def send_to_jira(sent_report: Report) -> list:
        assert sent_report.id == report.id
        sent_by.append("jira")
        return []

    def send_to_portal(sent_report: Report) -> list:
        assert sent_report.id == report.id
        sent_by.append("portal")
        return []

    monkeypatch.setattr("builtins.input", answer)
    monkeypatch.setattr(jira_service, "set_worklog", send_to_jira)
    monkeypatch.setattr(qatestlab_portal_service, "send_tasks", send_to_portal)

    result = run_cli("send", "20.08.2026", "--jira", "--portal")

    assert questions == [SEND_QUESTION]
    assert sent_by == ["jira", "portal"]
    assert result.exit_code == 0
    assert result.out == question_text() + "Jira\n\nQATestLab Portal\n"


def test_send_stops_when_the_question_is_declined(
    monkeypatch: pytest.MonkeyPatch,
    reporting_config: ReportingConfigFixture,
    run_cli: RunCli,
) -> None:
    reporting_config({"app": {"timezone": "UTC"}})
    ReportFactory.create(date=REPORT_DATE, id=1, tasks=[])
    sent_reports: list[Report] = []

    def record_send(report: Report) -> list:
        sent_reports.append(report)
        return []

    monkeypatch.setattr("builtins.input", lambda question: "n")
    monkeypatch.setattr(jira_service, "set_worklog", record_send)
    monkeypatch.setattr(qatestlab_portal_service, "send_tasks", record_send)

    result = run_cli("send", "20.08.2026", "--jira", "--portal")

    assert sent_reports == []
    assert result.exit_code == 0
    assert result.out == question_text()


def test_send_does_not_ask_for_a_report_of_today(
    monkeypatch: pytest.MonkeyPatch,
    reporting_config: ReportingConfigFixture,
    run_cli: RunCli,
) -> None:
    reporting_config({"app": {"timezone": "UTC"}})
    ReportFactory.create(date=datetime.datetime.now(datetime.UTC).date(), id=1, tasks=[])
    questions: list[str] = []

    def answer(question: str) -> str:
        questions.append(question)
        return "y"

    monkeypatch.setattr("builtins.input", answer)
    monkeypatch.setattr(jira_service, "set_worklog", lambda report: [])
    monkeypatch.setattr(qatestlab_portal_service, "send_tasks", lambda report: [])

    result = run_cli("send", "--jira", "--portal")

    assert questions == []
    assert result.exit_code == 0
    assert result.out == "Jira\n\nQATestLab Portal\n"


def test_send_without_a_report_fails(
    reporting_config: ReportingConfigFixture,
    run_cli: RunCli,
) -> None:
    reporting_config({"app": {"timezone": "UTC"}})

    failure = run_cli("send", "--jira", "--portal")

    assert failure.exit_code == 1
    assert failure.out == ""
    assert failure.err == "Report does not exist\n"


def test_send_without_a_target_fails(run_cli: RunCli) -> None:
    failure = run_cli("send")

    assert failure.exit_code == 1
    assert failure.out == ""
    assert "Specify at least one target" in failure.err


@pytest.mark.parametrize(
    "replacement_date",
    [
        pytest.param(None, id="report is gone"),
        pytest.param(datetime.date(2026, 1, 1), id="id belongs to another report"),
    ],
)
def test_send_stops_when_the_report_changed_while_answering(
    monkeypatch: pytest.MonkeyPatch,
    replacement_date: datetime.date | None,
    reporting_config: ReportingConfigFixture,
    run_cli: RunCli,
) -> None:
    reporting_config({"app": {"timezone": "UTC"}})
    ReportFactory.create(date=REPORT_DATE, id=1, tasks=[])
    replacement = None

    if replacement_date is not None:
        replacement = ReportFactory.create(date=replacement_date, id=2, tasks=[])

    monkeypatch.setattr("builtins.input", lambda question: "y")
    monkeypatch.setattr(report_service, "find_by_id", lambda session, report_id: replacement)

    failure = run_cli("send", "20.08.2026", "--jira")

    assert failure.exit_code == 1
    assert failure.out == question_text()
    assert failure.err == "Report changed, nothing was sent\n"


def test_send_reloads_the_confirmed_report_by_id(
    monkeypatch: pytest.MonkeyPatch,
    reporting_config: ReportingConfigFixture,
    run_cli: RunCli,
) -> None:
    reporting_config({"app": {"timezone": "UTC"}})
    ReportFactory.create(date=datetime.date(2026, 1, 1), id=1, tasks=[])
    ReportFactory.create(date=REPORT_DATE, id=2, tasks=[])
    sent_ids: list[int] = []

    def send_to_jira(sent_report: Report) -> list:
        sent_ids.append(sent_report.id)
        return []

    monkeypatch.setattr("builtins.input", lambda question: "y")
    monkeypatch.setattr(jira_service, "set_worklog", send_to_jira)

    result = run_cli("send", "20.08.2026", "--jira")

    assert result.exit_code == 0
    assert sent_ids == [2]
