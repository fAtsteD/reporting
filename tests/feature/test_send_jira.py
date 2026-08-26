import datetime

import jira.client
import jira.exceptions
import pytest

from reporting.database.models import Task
from tests import rendered_output
from tests.conftest import ReportingConfigFixture
from tests.factories import KindFactory, ProjectFactory, ReportFactory, TaskFactory
from tests.fixtures.cli import RunCli

EXIST_JIRA_KEY = "TEST-"
MISSING_JIRA_KEY = "NO-TEST-"


@pytest.mark.parametrize(
    "jira_keys",
    [
        pytest.param(
            [],
            id="no tasks",
        ),
        pytest.param(
            ["", "", ""],
            id="tasks are not for jira",
        ),
        pytest.param(
            ["NO-EXIST-1", "NO-EXIST-767", "NO-EXIST-567"],
            id="tasks with wrong key",
        ),
        pytest.param(
            ["NO-TEST-1", "NO-TEST-23", "NO-TEST-456456"],
            id="tasks with missing jira issues",
        ),
        pytest.param(
            ["TEST-1", "TEST-678", "TEST-6789"],
            id="some acceptable tasks",
        ),
        pytest.param(
            ["TEST-1", "NO-TEST-2345", "NO-EXIST-34", "TEST-234"],
            id="mix tasks",
        ),
    ],
)
def test_send_jira_report_with_jira_issues(
    jira_keys: list[str],
    monkeypatch: pytest.MonkeyPatch,
    reporting_config: ReportingConfigFixture,
    run_cli: RunCli,
) -> None:
    reporting_config(
        {
            "app": {
                "minute-round-to": 15,
                "timezone": "UTC",
            },
            "jira": {
                "issue-key-base": [EXIST_JIRA_KEY, MISSING_JIRA_KEY],
                "login": "login",
                "password": "password",
                "server": "https://jira.example.com",
            },
        }
    )
    kind = KindFactory.create(alias="dev", id=1, name="Develop", tasks=[])
    project = ProjectFactory.create(alias="mp", id=1, name="My Project", tasks=[])
    report = ReportFactory.create(date=datetime.datetime.now(datetime.UTC).date(), id=1, tasks=[])
    summaries: list[str] = []
    tasks: list[Task] = []

    for index, jira_key in enumerate(jira_keys):
        summary = f"{jira_key}: task {index}" if jira_key else f"task {index}"
        summaries.append(summary)
        tasks.append(
            TaskFactory.create(
                id=index + 1,
                kind=kind,
                kinds_id=kind.id,
                logged_seconds=60 * 60,
                project=project,
                projects_id=project.id,
                report=report,
                reports_id=report.id,
                summary=summary,
            )
        )

    issue_calls: list[str] = []
    worklog_calls: list[tuple[str, str]] = []

    def init_jira(*args, **kwargs) -> None:
        assert kwargs["server"] == "https://jira.example.com"
        assert kwargs["basic_auth"] == ("login", "password")

    def check_issue(self: jira.client.JIRA, key: str) -> bool:
        issue_calls.append(key)

        if key.startswith(EXIST_JIRA_KEY):
            return True

        raise jira.exceptions.JIRAError()

    def check_add_worklog(self: jira.client.JIRA, key: str, time_spent: str) -> bool:
        worklog_calls.append((key, time_spent))
        return True

    monkeypatch.setattr(jira.client.JIRA, "__init__", init_jira)
    monkeypatch.setattr(jira.client.JIRA, "issue", check_issue)
    monkeypatch.setattr(jira.client.JIRA, "add_worklog", check_add_worklog)

    result = run_cli("send", "--jira")
    expected_failures = [key for key in jira_keys if key.startswith(MISSING_JIRA_KEY)]

    if expected_failures:
        assert result.exit_code == 1
        assert result.err == f"Failed tasks: {len(expected_failures)}\n"
    else:
        assert result.exit_code == 0

    expected_attempted = [key for key in jira_keys if key.startswith((EXIST_JIRA_KEY, MISSING_JIRA_KEY))]
    expected_logged = [key for key in jira_keys if key.startswith(EXIST_JIRA_KEY)]
    assert issue_calls == expected_attempted
    assert [key for key, _ in worklog_calls] == expected_logged
    assert [time_spent for _, time_spent in worklog_calls] == ["1h 0m"] * len(expected_logged)

    expected_cells = [["Jira"]]

    for jira_key, summary in zip(jira_keys, summaries):
        if jira_key.startswith(EXIST_JIRA_KEY):
            expected_cells.append(["\u2713", "01:00", summary, "My Project"])
        elif jira_key.startswith(MISSING_JIRA_KEY):
            expected_cells.append(["\u2717", "01:00", summary, "My Project"])

    if len(expected_cells) == 1:
        expected_cells.append(["No tasks to send"])

    assert rendered_output.cells(result.out) == expected_cells


def test_send_jira_shows_the_failure_reason(
    monkeypatch: pytest.MonkeyPatch,
    reporting_config: ReportingConfigFixture,
    run_cli: RunCli,
) -> None:
    reporting_config(
        {
            "app": {
                "minute-round-to": 15,
                "timezone": "UTC",
            },
            "jira": {
                "issue-key-base": [EXIST_JIRA_KEY],
                "login": "login",
                "password": "password",
                "server": "https://jira.example.com",
            },
        }
    )
    kind = KindFactory.create(alias="dev", id=1, name="Develop", tasks=[])
    project = ProjectFactory.create(alias="mp", id=1, name="My Project", tasks=[])
    report = ReportFactory.create(date=datetime.datetime.now(datetime.UTC).date(), id=1, tasks=[])
    TaskFactory.create(
        id=1,
        kind=kind,
        kinds_id=kind.id,
        logged_seconds=60 * 60,
        project=project,
        projects_id=project.id,
        report=report,
        reports_id=report.id,
        summary="TEST-1: task 0",
    )

    def refuse_issue(self: jira.client.JIRA, key: str) -> bool:
        raise jira.exceptions.JIRAError(status_code=404, text="Issue does not exist")

    monkeypatch.setattr(jira.client.JIRA, "__init__", lambda *args, **kwargs: None)
    monkeypatch.setattr(jira.client.JIRA, "issue", refuse_issue)

    failure = run_cli("send", "--jira")

    assert failure.exit_code == 1
    assert failure.err == "Failed tasks: 1\n"
    assert rendered_output.cells(failure.out) == [
        ["Jira"],
        ["\u2717", "01:00", "TEST-1: task 0", "My Project"],
        ["Issue does not exist"],
    ]
