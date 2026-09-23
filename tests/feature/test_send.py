import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Session

from reporting.cli.views.view_message import SEND_QUESTION
from reporting.database.models import Report
from tests.assertions import cli_output
from tests.factories.database import KindFactory, ProjectFactory, ReportFactory, TaskFactory
from tests.fixtures.cli import ConfirmationFake, RunCli
from tests.fixtures.jira import JIRA_CONFIG, JiraApiFake
from tests.fixtures.portal import PORTAL_CONFIG, PortalApiFake
from tests.fixtures.reporting_config import ReportingConfigFixture

_HOUR_SECONDS = 60 * 60
_PAST_DATE = datetime.date(2026, 8, 20)


def test_send_asks_one_question_for_both_targets(
    confirmation: ConfirmationFake,
    jira_api: JiraApiFake,
    portal_api: PortalApiFake,
    reporting_config: ReportingConfigFixture,
    run_cli: RunCli,
) -> None:
    reporting_config(_both_targets_config())
    ReportFactory.create(date=_PAST_DATE)
    confirmation.answer("y")

    result = run_cli("send", "20.08.2026", "--jira", "--portal")

    assert confirmation.questions == [SEND_QUESTION]
    assert result.exit_code == 0
    assert "No tasks to send" in cli_output.flat_text(result.out)


def test_send_does_not_ask_for_a_report_of_today(
    confirmation: ConfirmationFake,
    jira_api: JiraApiFake,
    portal_api: PortalApiFake,
    reporting_config: ReportingConfigFixture,
    run_cli: RunCli,
    today: datetime.date,
) -> None:
    reporting_config(_both_targets_config())
    ReportFactory.create(date=today)

    result = run_cli("send", "--jira", "--portal")

    assert confirmation.questions == []
    assert result.exit_code == 0


def test_send_fails_when_no_report_exists(
    reporting_config: ReportingConfigFixture,
    run_cli: RunCli,
) -> None:
    reporting_config(_both_targets_config())

    failure = run_cli("send", "--jira", "--portal")

    assert failure.exit_code == 1
    assert failure.out == ""
    assert failure.err == "Report does not exist\n"


def test_send_fails_when_no_target_is_given(run_cli: RunCli) -> None:
    failure = run_cli("send")

    assert failure.exit_code == 1
    assert failure.out == ""
    assert "Specify at least one target" in failure.err


def test_send_jira_prints_every_result_and_exits_with_one_when_a_task_failed(
    jira_api: JiraApiFake,
    reporting_config: ReportingConfigFixture,
    run_cli: RunCli,
    today: datetime.date,
) -> None:
    reporting_config(JIRA_CONFIG)
    report = ReportFactory.create(date=today)
    project = ProjectFactory.create(name="My Project")
    TaskFactory.create(logged_seconds=_HOUR_SECONDS, project=project, report=report, summary="TEST-1: wrote the parser")
    TaskFactory.create(logged_seconds=_HOUR_SECONDS, project=project, report=report, summary="TEST-404: wrote the docs")
    jira_api.add_issue("TEST-1", "Summary of the issue")
    jira_api.fail_issue("TEST-404", status_code=404, text="Issue does not exist")

    failure = run_cli("send", "--jira")

    assert failure.exit_code == 1
    assert failure.err == "Failed tasks: 1\n"
    cli_output.assert_lines(
        failure.out,
        [
            "Jira",
            "✓ 01:00 TEST-1: wrote the parser My Project",
            "✗ 01:00 TEST-404: wrote the docs My Project",
            "Issue does not exist",
        ],
    )


def test_send_portal_prints_every_result(
    portal_api: PortalApiFake,
    portal_config: None,
    run_cli: RunCli,
    today: datetime.date,
) -> None:
    report = ReportFactory.create(date=today)
    TaskFactory.create(
        kind=KindFactory.create(name="Develop"),
        logged_seconds=_HOUR_SECONDS,
        project=ProjectFactory.create(name="My Project"),
        report=report,
        summary="wrote the parser",
    )
    portal_api.add_category("Develop")

    result = run_cli("send", "--portal")

    assert result.exit_code == 0
    cli_output.assert_lines(result.out, ["QATestLab Portal", "✓ 01:00 wrote the parser My Project"])


def test_send_stops_when_the_question_is_declined(
    confirmation: ConfirmationFake,
    jira_api: JiraApiFake,
    portal_api: PortalApiFake,
    reporting_config: ReportingConfigFixture,
    run_cli: RunCli,
) -> None:
    reporting_config(_both_targets_config())
    report = ReportFactory.create(date=_PAST_DATE)
    TaskFactory.create(logged_seconds=_HOUR_SECONDS, report=report, summary="TEST-1: a task")
    jira_api.add_issue("TEST-1", "Summary of the issue")
    confirmation.answer("n")

    result = run_cli("send", "20.08.2026", "--jira", "--portal")

    assert result.exit_code == 0
    assert jira_api.worklogs == []
    assert portal_api.sent_time_records == []


def test_send_stops_when_the_report_date_changed_while_answering(
    confirmation: ConfirmationFake,
    database_session: Session,
    jira_api: JiraApiFake,
    reporting_config: ReportingConfigFixture,
    run_cli: RunCli,
) -> None:
    reporting_config(_both_targets_config())
    report = ReportFactory.create(date=_PAST_DATE)

    def move_the_report(question: str) -> str:
        database_session.execute(sa.update(Report).where(Report.id == report.id).values(date=datetime.date(2026, 1, 1)))
        database_session.commit()

        return "y"

    confirmation.answer_with(move_the_report)

    failure = run_cli("send", "20.08.2026", "--jira")

    assert failure.exit_code == 1
    assert failure.err == "Report changed, nothing was sent\n"
    assert jira_api.worklogs == []


def test_send_stops_when_the_report_is_gone_while_answering(
    confirmation: ConfirmationFake,
    database_session: Session,
    jira_api: JiraApiFake,
    reporting_config: ReportingConfigFixture,
    run_cli: RunCli,
) -> None:
    reporting_config(_both_targets_config())
    report = ReportFactory.create(date=_PAST_DATE)

    def delete_the_report(question: str) -> str:
        database_session.execute(sa.delete(Report).where(Report.id == report.id))
        database_session.commit()

        return "y"

    confirmation.answer_with(delete_the_report)

    failure = run_cli("send", "20.08.2026", "--jira")

    assert failure.exit_code == 1
    assert failure.err == "Report changed, nothing was sent\n"
    assert jira_api.worklogs == []


def _both_targets_config() -> dict:
    return {
        "app": {"timezone": "UTC"},
        "jira": JIRA_CONFIG["jira"],
        "qatestlab-portal": PORTAL_CONFIG["qatestlab-portal"],
    }
