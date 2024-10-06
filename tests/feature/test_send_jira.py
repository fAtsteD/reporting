import faker
import jira.client
import jira.exceptions
import pytest
from sqlalchemy.orm import Session

from reporting import cli
from tests.conftest import ReportingConfigFixture, TaskFixture


def test_send_jira_empty_report(
    capsys: pytest.CaptureFixture,
    reporting_config: ReportingConfigFixture,
    database_session: Session,
    monkeypatch: pytest.MonkeyPatch,
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
    reporting_config: ReportingConfigFixture,
    database_session: Session,
    monkeypatch: pytest.MonkeyPatch,
    add_task: TaskFixture,
    faker: faker.Faker,
    jira_keys: list[str],
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
    output_expected = "Jira\n"
    tasks = []

    for jira_key in jira_keys:
        task_summary = faker.sentence()
        is_jira_key = False

        if jira_key:
            task_summary = f"{jira_key}: {task_summary}"
            is_jira_key = any(map(lambda allowed_jira_key: jira_key.startswith(allowed_jira_key), allowed_jira_keys))

            if is_jira_key:
                output_expected += "[+] " if jira_key.startswith(exist_jira_key) else "[-] "

        task = add_task(summary=task_summary)
        output_expected += f"{task}\n" if jira_key and is_jira_key else ""
        tasks.append(task)

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
    assert output.out == f"{output_expected}\n"
