import pytest
from sqlalchemy.orm import Session

from reporting.database.models import Report
from reporting.services.jira import jira_service
from reporting.services.jira.exceptions import JiraNotConfiguredError
from reporting.services.jira.models import JiraTaskStatus
from tests.factories.database import KindFactory, ProjectFactory, ReportFactory, TaskFactory
from tests.fixtures.jira import JIRA_CONFIG, JIRA_LOGIN, JIRA_PASSWORD, JIRA_SERVER, JiraApiFake, Worklog
from tests.fixtures.reporting_config import ReportingConfigFixture

_HOUR_SECONDS = 60 * 60
_ISSUE_SUMMARY = "Summary of the issue"


def test_authenticates_with_the_configured_server_and_account(
    database_session: Session,
    jira_api: JiraApiFake,
    jira_config: None,
) -> None:
    jira_service.set_worklog(ReportFactory.create())

    assert jira_api.connections == [{"server": JIRA_SERVER, "basic_auth": (JIRA_LOGIN, JIRA_PASSWORD)}]


def test_describes_a_key_without_any_text_as_the_key_alone(
    database_session: Session,
    jira_api: JiraApiFake,
    jira_config: None,
) -> None:
    report = ReportFactory.create()
    TaskFactory.create(logged_seconds=_HOUR_SECONDS, report=report, summary="TEST-1:   ")
    jira_api.add_issue("TEST-1", _ISSUE_SUMMARY)

    results = jira_service.set_worklog(report)

    assert results[0].merged_task.description == "TEST-1:"


def test_fails_when_jira_is_not_configured(
    database_session: Session,
) -> None:
    with pytest.raises(JiraNotConfiguredError):
        jira_service.set_worklog(ReportFactory.create())


@pytest.mark.parametrize(
    "texts, comment",
    [
        pytest.param([_ISSUE_SUMMARY], None, id="the only text is the issue summary"),
        pytest.param([_ISSUE_SUMMARY.lower()], None, id="the issue summary in another case"),
        pytest.param([_ISSUE_SUMMARY, "extra work"], "extra work", id="the issue summary and another text"),
        pytest.param(["extra work", "more work"], "- extra work\n- more work", id="texts without the issue summary"),
    ],
)
def test_leaves_the_issue_summary_out_of_the_worklog_comment(
    comment: str | None,
    database_session: Session,
    jira_api: JiraApiFake,
    jira_config: None,
    texts: list[str],
) -> None:
    report = _create_report_of_texts(texts)
    jira_api.add_issue("TEST-1", _ISSUE_SUMMARY)

    jira_service.set_worklog(report)

    assert [worklog.comment for worklog in jira_api.worklogs] == [comment]


def test_logs_the_time_spent_on_a_task_with_a_configured_issue_key(
    database_session: Session,
    jira_api: JiraApiFake,
    jira_config: None,
) -> None:
    report = ReportFactory.create()
    TaskFactory.create(logged_seconds=_HOUR_SECONDS, report=report, summary="TEST-1: wrote the parser")
    jira_api.add_issue("TEST-1", _ISSUE_SUMMARY)

    results = jira_service.set_worklog(report)

    assert jira_api.worklogs == [Worklog(comment="wrote the parser", key="TEST-1", time_spent="1h 0m")]
    assert [result.status for result in results] == [JiraTaskStatus.SENT]


def test_merges_tasks_with_the_same_key_into_one_worklog(
    database_session: Session,
    jira_api: JiraApiFake,
    jira_config: None,
) -> None:
    kind = KindFactory.create(alias="dev", name="Develop")
    other_kind = KindFactory.create(alias="rev", name="Review")
    project = ProjectFactory.create(alias="mp", name="My Project")
    other_project = ProjectFactory.create(alias="op", name="Other Project")
    report = ReportFactory.create()
    TaskFactory.create(
        kind=kind, logged_seconds=_HOUR_SECONDS, project=project, report=report, summary="TEST-1: text a"
    )
    TaskFactory.create(
        kind=other_kind, logged_seconds=_HOUR_SECONDS, project=other_project, report=report, summary="TEST-1: text b"
    )
    TaskFactory.create(
        kind=other_kind, logged_seconds=_HOUR_SECONDS, project=project, report=report, summary="TEST-1: text a"
    )
    jira_api.add_issue("TEST-1", _ISSUE_SUMMARY)

    results = jira_service.set_worklog(report)

    assert jira_api.requested_issue_keys == ["TEST-1"]
    assert jira_api.worklogs == [Worklog(comment="- text a\n- text b", key="TEST-1", time_spent="3h 0m")]
    assert results[0].merged_task.description == "TEST-1:\n- text a\n- text b"
    assert results[0].merged_task.project_names == "My Project, Other Project"


def test_reports_a_task_whose_issue_does_not_exist_as_failed(
    database_session: Session,
    jira_api: JiraApiFake,
    jira_config: None,
) -> None:
    report = ReportFactory.create()
    TaskFactory.create(logged_seconds=_HOUR_SECONDS, report=report, summary="TEST-404: wrote the parser")
    jira_api.fail_issue("TEST-404", status_code=404, text="Issue does not exist")

    results = jira_service.set_worklog(report)

    assert [(result.status, result.reason) for result in results] == [(JiraTaskStatus.FAILED, "Issue does not exist")]
    assert jira_api.worklogs == []


def test_returns_no_result_for_a_report_without_tasks(
    database_session: Session,
    jira_api: JiraApiFake,
    jira_config: None,
) -> None:
    results = jira_service.set_worklog(ReportFactory.create())

    assert results == []
    assert jira_api.worklogs == []


def test_rounds_the_logged_time_to_the_configured_minutes(
    database_session: Session,
    jira_api: JiraApiFake,
    reporting_config: ReportingConfigFixture,
) -> None:
    reporting_config(JIRA_CONFIG | {"app": {"minute-round-to": 15, "timezone": "UTC"}})
    report = ReportFactory.create()
    TaskFactory.create(logged_seconds=53 * 60, report=report, summary="TEST-1: wrote the parser")
    jira_api.add_issue("TEST-1", _ISSUE_SUMMARY)

    jira_service.set_worklog(report)

    assert [worklog.time_spent for worklog in jira_api.worklogs] == ["1h 0m"]


def test_sends_the_tasks_it_can_when_another_task_fails(
    database_session: Session,
    jira_api: JiraApiFake,
    jira_config: None,
) -> None:
    report = ReportFactory.create()
    TaskFactory.create(logged_seconds=_HOUR_SECONDS, report=report, summary="TEST-1: wrote the parser")
    TaskFactory.create(logged_seconds=_HOUR_SECONDS, report=report, summary="TEST-404: wrote the docs")
    jira_api.add_issue("TEST-1", _ISSUE_SUMMARY)
    jira_api.fail_issue("TEST-404", status_code=404, text="Issue does not exist")

    results = jira_service.set_worklog(report)

    assert [result.status for result in results] == [JiraTaskStatus.SENT, JiraTaskStatus.FAILED]
    assert jira_api.worklogs == [Worklog(comment="wrote the parser", key="TEST-1", time_spent="1h 0m")]


def test_skips_a_task_whose_key_is_not_a_configured_issue_key(
    database_session: Session,
    jira_api: JiraApiFake,
    jira_config: None,
) -> None:
    report = ReportFactory.create()
    TaskFactory.create(logged_seconds=_HOUR_SECONDS, report=report, summary="OTHER-1: wrote the parser")
    jira_api.add_issue("OTHER-1", _ISSUE_SUMMARY)

    results = jira_service.set_worklog(report)

    assert results == []
    assert jira_api.requested_issue_keys == []
    assert jira_api.worklogs == []


def test_skips_a_task_without_a_key(
    database_session: Session,
    jira_api: JiraApiFake,
    jira_config: None,
) -> None:
    report = ReportFactory.create()
    TaskFactory.create(logged_seconds=_HOUR_SECONDS, report=report, summary="wrote the parser")

    results = jira_service.set_worklog(report)

    assert results == []
    assert jira_api.requested_issue_keys == []
    assert jira_api.worklogs == []


def _create_report_of_texts(texts: list[str]) -> Report:
    report = ReportFactory.create()

    for text in texts:
        TaskFactory.create(logged_seconds=_HOUR_SECONDS, report=report, summary=f"TEST-1: {text}")

    return report
