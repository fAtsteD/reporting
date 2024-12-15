import faker
import jira.client
import jira.exceptions
import pytest

from reporting import cli
from reporting.models.report import Report
from reporting.models.task import Task
from tests.conftest import ReportingConfigFixture
from tests.factories import ReportFactory, TaskFactory


def test_send_jira_empty_report(
    capsys: pytest.CaptureFixture,
    monkeypatch: pytest.MonkeyPatch,
    reporting_config: ReportingConfigFixture,
) -> None:
    reporting_config(
        {
            "jira": {
                "issue_key_bases": [],
                "login": "login",
                "password": "password",
                "server": "server",
            }
        }
    )
    monkeypatch.setattr(jira.client.JIRA, "issue", lambda: None)
    monkeypatch.setattr(jira.client.JIRA, "add_worklog", lambda: None)
    output_expected = "Jira\n"

    cli.main(["--jira"])

    output = capsys.readouterr()
    assert output.out == output_expected


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
    capsys: pytest.CaptureFixture,
    faker: faker.Faker,
    jira_keys: list[str],
    monkeypatch: pytest.MonkeyPatch,
    reporting_config: ReportingConfigFixture,
) -> None:
    exist_jira_key = "TEST-"
    allowed_jira_keys = [
        exist_jira_key,
        "NO-TEST-",
    ]
    reporting_config(
        {
            "jira": {
                "issue-key-base": allowed_jira_keys,
                "login": "login",
                "password": "password",
                "server": "https://jira.example.com",
            },
            "minute-round-to": 15,
        }
    )
    report: Report = ReportFactory.create(tasks=[])
    tasks: list[Task] = []

    for jira_key in jira_keys:
        task_summary = faker.sentence(nb_words=10, variable_nb_words=True)

        if jira_key:
            task_summary = f"{jira_key}: {task_summary}"

        tasks.append(TaskFactory.create(report=report, reports_id=report.id, summary=task_summary))

    def init_jira(*args, **kwargs) -> None:
        assert kwargs["server"] == "https://jira.example.com"
        assert kwargs["basic_auth"] == ("login", "password")

    def check_issue_key(self: jira.client.JIRA, key: str, timeSpent: str | None = None) -> bool:
        assert key in jira_keys

        if timeSpent is not None:
            assert len(timeSpent) > 0

        if key.startswith(exist_jira_key):
            return True

        raise jira.exceptions.JIRAError()

    monkeypatch.setattr(jira.client.JIRA, "__init__", init_jira)
    monkeypatch.setattr(jira.client.JIRA, "issue", check_issue_key)
    monkeypatch.setattr(jira.client.JIRA, "add_worklog", check_issue_key)

    cli.main(["--jira"])

    output = capsys.readouterr()
    assert str(output.out).startswith("Jira\n")

    for task in tasks:
        is_jira_key = any(map(lambda allowed_jira_key: task.summary.startswith(allowed_jira_key), allowed_jira_keys))

        if is_jira_key:
            if task.summary.startswith(exist_jira_key):
                assert output.out.find(f"[+] {task}\n") > -1
            else:
                assert output.out.find(f"[-] {task}\n") > -1
        else:
            assert output.out.find(f"{task}\n") == -1
