import datetime

import jira.client
import jira.exceptions
import pytest

from reporting.database.models import Kind, Project, Report, Task
from tests import rendered_output
from tests.conftest import ReportingConfigFixture
from tests.factories import KindFactory, ProjectFactory, ReportFactory, TaskFactory
from tests.fixtures.cli import RunCli
from tests.fixtures.jira import JiraFixture

EXIST_JIRA_KEY = "TEST-"
ISSUE_SUMMARY = "Summary of the issue"
JIRA_LOGIN = "login"
JIRA_PASSWORD = "password"
JIRA_SERVER = "https://jira.example.com"
MISSING_JIRA_KEY = "NO-TEST-"


def configure_jira(reporting_config: ReportingConfigFixture, issue_key_bases: list[str]) -> None:
    reporting_config(
        {
            "app": {
                "minute-round-to": 15,
                "timezone": "UTC",
            },
            "jira": {
                "issue-key-base": issue_key_bases,
                "login": JIRA_LOGIN,
                "password": JIRA_PASSWORD,
                "server": JIRA_SERVER,
            },
        }
    )


def create_report() -> Report:
    return ReportFactory.create(date=datetime.datetime.now(datetime.UTC).date(), tasks=[])


def create_task(summary: str, logged_seconds: int, kind: Kind, project: Project, report: Report) -> Task:
    return TaskFactory.create(
        kind=kind,
        kinds_id=kind.id,
        logged_seconds=logged_seconds,
        project=project,
        projects_id=project.id,
        report=report,
        reports_id=report.id,
        summary=summary,
    )


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
    jira_mock: JiraFixture,
    reporting_config: ReportingConfigFixture,
    run_cli: RunCli,
) -> None:
    configure_jira(reporting_config, [EXIST_JIRA_KEY, MISSING_JIRA_KEY])
    kind = KindFactory.create(alias="dev", name="Develop", tasks=[])
    project = ProjectFactory.create(alias="mp", name="My Project", tasks=[])
    report = create_report()
    summaries: list[str] = []

    for index, jira_key in enumerate(jira_keys):
        summary = f"{jira_key}: task {index}" if jira_key else f"task {index}"
        summaries.append(summary)
        create_task(summary, 60 * 60, kind, project, report)

    calls = jira_mock(issue_summary=ISSUE_SUMMARY, existing_key_prefix=EXIST_JIRA_KEY)

    result = run_cli("send", "--jira")
    expected_failures = [key for key in jira_keys if key.startswith(MISSING_JIRA_KEY)]

    if expected_failures:
        assert result.exit_code == 1
        assert result.err == f"Failed tasks: {len(expected_failures)}\n"
    else:
        assert result.exit_code == 0

    expected_worklogs = [
        (key, "1h 0m", f"task {index}") for index, key in enumerate(jira_keys) if key.startswith(EXIST_JIRA_KEY)
    ]
    assert calls.init_arguments == {"server": JIRA_SERVER, "basic_auth": (JIRA_LOGIN, JIRA_PASSWORD)}
    assert calls.issue_keys == [key for key in jira_keys if key.startswith((EXIST_JIRA_KEY, MISSING_JIRA_KEY))]
    assert calls.worklogs == expected_worklogs

    expected_cells = [["Jira"]]

    for jira_key, summary in zip(jira_keys, summaries):
        if jira_key.startswith(EXIST_JIRA_KEY):
            expected_cells.append(["✓", "01:00", summary, "My Project"])
        elif jira_key.startswith(MISSING_JIRA_KEY):
            expected_cells.append(["✗", "01:00", summary, "My Project"])

    if len(expected_cells) == 1:
        expected_cells.append(["No tasks to send"])

    assert rendered_output.cells(result.out) == expected_cells


@pytest.mark.parametrize(
    "texts, comment",
    [
        pytest.param([ISSUE_SUMMARY], None, id="the only text is the summary"),
        pytest.param([ISSUE_SUMMARY.lower()], None, id="the only text is the summary in another case"),
        pytest.param([ISSUE_SUMMARY, "extra work"], "extra work", id="the summary and another text"),
        pytest.param(["extra work", "more work"], "- extra work\n- more work", id="texts without the summary"),
    ],
)
def test_send_jira_leaves_the_issue_summary_out_of_the_comment(
    comment: str | None,
    jira_mock: JiraFixture,
    reporting_config: ReportingConfigFixture,
    run_cli: RunCli,
    texts: list[str],
) -> None:
    configure_jira(reporting_config, [EXIST_JIRA_KEY])
    kind = KindFactory.create(alias="dev", name="Develop", tasks=[])
    project = ProjectFactory.create(alias="mp", name="My Project", tasks=[])
    report = create_report()

    for text in texts:
        create_task(f"TEST-1: {text}", 60 * 60, kind, project, report)

    calls = jira_mock(issue_summary=ISSUE_SUMMARY)

    result = run_cli("send", "--jira")

    assert result.exit_code == 0
    assert [worklog_comment for _, _, worklog_comment in calls.worklogs] == [comment]


def test_send_jira_merges_tasks_with_the_same_key_into_one_worklog(
    jira_mock: JiraFixture,
    reporting_config: ReportingConfigFixture,
    run_cli: RunCli,
) -> None:
    configure_jira(reporting_config, [EXIST_JIRA_KEY])
    kind = KindFactory.create(alias="dev", name="Develop", tasks=[])
    other_kind = KindFactory.create(alias="rev", name="Review", tasks=[])
    project = ProjectFactory.create(alias="mp", name="My Project", tasks=[])
    other_project = ProjectFactory.create(alias="op", name="Other Project", tasks=[])
    report = create_report()
    create_task("TEST-1: text a", 60 * 60, kind, project, report)
    create_task("TEST-1: text b", 60 * 60, other_kind, other_project, report)
    create_task("TEST-1: text a", 60 * 60, other_kind, project, report)
    calls = jira_mock(issue_summary=ISSUE_SUMMARY)

    result = run_cli("send", "--jira")

    assert result.exit_code == 0
    assert calls.issue_keys == ["TEST-1"]
    assert calls.worklogs == [("TEST-1", "3h 0m", "- text a\n- text b")]
    assert rendered_output.cells(result.out) == [
        ["Jira"],
        ["✓", "03:00", "TEST-1:", "My Project, Other Project"],
        ["- text a"],
        ["- text b"],
    ]


def test_send_jira_shows_the_failure_reason(
    monkeypatch: pytest.MonkeyPatch,
    reporting_config: ReportingConfigFixture,
    run_cli: RunCli,
) -> None:
    configure_jira(reporting_config, [EXIST_JIRA_KEY])
    kind = KindFactory.create(alias="dev", name="Develop", tasks=[])
    project = ProjectFactory.create(alias="mp", name="My Project", tasks=[])
    report = create_report()
    create_task("TEST-1: task 0", 60 * 60, kind, project, report)

    def refuse_issue(self: jira.client.JIRA, key: str) -> bool:
        raise jira.exceptions.JIRAError(status_code=404, text="Issue does not exist")

    monkeypatch.setattr(jira.client.JIRA, "__init__", lambda *args, **kwargs: None)
    monkeypatch.setattr(jira.client.JIRA, "issue", refuse_issue)

    failure = run_cli("send", "--jira")

    assert failure.exit_code == 1
    assert failure.err == "Failed tasks: 1\n"
    assert rendered_output.cells(failure.out) == [
        ["Jira"],
        ["✗", "01:00", "TEST-1: task 0", "My Project"],
        ["Issue does not exist"],
    ]


def test_send_jira_skips_a_key_that_is_not_a_configured_issue_key(
    jira_mock: JiraFixture,
    reporting_config: ReportingConfigFixture,
    run_cli: RunCli,
) -> None:
    configure_jira(reporting_config, [EXIST_JIRA_KEY])
    kind = KindFactory.create(alias="dev", name="Develop", tasks=[])
    project = ProjectFactory.create(alias="mp", name="My Project", tasks=[])
    report = create_report()
    create_task("OTHER-1: text a", 60 * 60, kind, project, report)
    calls = jira_mock(issue_summary=ISSUE_SUMMARY)

    result = run_cli("send", "--jira")

    assert result.exit_code == 0
    assert calls.issue_keys == []
    assert calls.worklogs == []
    assert rendered_output.cells(result.out) == [["Jira"], ["No tasks to send"]]
