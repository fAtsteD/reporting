import json

import pytest

from reporting import config
from reporting.config import config_access, config_file
from tests.conftest import ReportingConfigFixture
from tests.fixtures.cli import RunCli


def test_list_shows_config_file_path(
    reporting_config: ReportingConfigFixture,
    run_cli: RunCli,
) -> None:
    config_path = config_file.config_path()

    missing = run_cli("config", "list")
    assert missing.out.startswith(f"Config file: {config_path} (does not exist, every value is a default)\n")

    reporting_config()

    existing = run_cli("config", "list")
    assert existing.out.startswith(f"Config file: {config_path}\n")


def test_list_shows_every_setting_with_description(
    reporting_config: ReportingConfigFixture,
    run_cli: RunCli,
) -> None:
    reporting_config()

    result = run_cli("config", "list")

    for key, _, description in config_access.iterate_values(config.current):
        assert key in result.out
        assert description, f"{key} does not have a description"
        assert description in result.out


@pytest.mark.parametrize(
    "key, value, expected",
    [
        pytest.param("app.timezone", "Europe/Kyiv", "Europe/Kyiv", id="text"),
        pytest.param("app.minute-round-to", "25", "25", id="number"),
        pytest.param("dictionary.task.l", "lunch", "lunch", id="dictionary entry"),
    ],
)
def test_set_and_get_value(
    expected: str,
    key: str,
    reporting_config: ReportingConfigFixture,
    run_cli: RunCli,
    value: str,
) -> None:
    reporting_config()

    assert run_cli("config", "set", key, value).out == f"{key} = {expected}\n"
    assert run_cli("config", "get", key).out == f"{expected}\n"


def test_get_section_prints_a_json_object(
    reporting_config: ReportingConfigFixture,
    run_cli: RunCli,
) -> None:
    reporting_config({"jira": {"login": "someone", "server": "https://jira.example.com"}})

    result = run_cli("config", "get", "jira")

    assert (
        result.out
        == '{"issue-key-base": [], "login": "someone", "password": "", "server": "https://jira.example.com"}\n'
    )


def test_set_saves_value_in_the_config_file(
    reporting_config: ReportingConfigFixture,
    run_cli: RunCli,
) -> None:
    reporting_config()

    run_cli("config", "set", "app.minute-round-to", "25")

    saved = json.loads(config_file.config_path().read_text(encoding="utf-8"))
    assert saved["app"]["minute-round-to"] == 25


@pytest.mark.parametrize(
    "key, expected",
    [
        pytest.param("jira.password", "", id="text returns to default"),
        pytest.param("dictionary.task.l", "null", id="dictionary entry is removed"),
        pytest.param(
            "jira",
            '{"issue-key-base": [], "login": "", "password": "", "server": ""}',
            id="whole section is reset",
        ),
    ],
)
def test_unset_returns_value_to_default(
    expected: str,
    key: str,
    reporting_config: ReportingConfigFixture,
    run_cli: RunCli,
) -> None:
    reporting_config(
        {
            "dictionary": {"task": {"l": "lunch"}},
            "jira": {"password": "secret"},
        }
    )

    run_cli("config", "unset", key)

    assert run_cli("config", "get", key).out == f"{expected}\n"


def test_set_and_unset_list_items(
    reporting_config: ReportingConfigFixture,
    run_cli: RunCli,
) -> None:
    reporting_config()

    assert run_cli("config", "set", "app.omit-task", "lunch").out == 'app.omit-task = ["lunch"]\n'
    assert run_cli("config", "set", "app.omit-task", "break").out == 'app.omit-task = ["lunch", "break"]\n'
    assert run_cli("config", "set", "app.omit-task", "lunch").out == 'app.omit-task = ["lunch", "break"]\n'
    assert run_cli("config", "unset", "app.omit-task", "lunch").out == 'app.omit-task = ["break"]\n'
    assert run_cli("config", "unset", "app.omit-task").out == "app.omit-task = []\n"


def test_set_adds_json_array_as_one_list_item(
    reporting_config: ReportingConfigFixture,
    run_cli: RunCli,
) -> None:
    reporting_config()

    result = run_cli("config", "set", "app.omit-task", '["a","b"]')

    assert result.out == 'app.omit-task = ["[\\"a\\",\\"b\\"]"]\n'


@pytest.mark.parametrize(
    "arguments, expected_message",
    [
        pytest.param(["config", "get", "unknown.key"], "Unknown configuration key", id="unknown key"),
        pytest.param(["config", "set", "app.minute-round-to", "abc"], "app.minute-round-to", id="wrong type"),
        pytest.param(["config", "set", "dictionary.task", "lunch"], "is a group of values", id="dictionary itself"),
        pytest.param(["config", "unset", "app.minute-round-to", "x"], "is not a list", id="value for not a list"),
        pytest.param(["config", "unset", "app.omit-task", "nope"], '"nope" is not in app.omit-task', id="missing item"),
    ],
)
def test_command_fails_with_message(
    arguments: list[str],
    expected_message: str,
    reporting_config: ReportingConfigFixture,
    run_cli: RunCli,
) -> None:
    reporting_config({"app": {"omit-task": ["lunch"]}})

    failure = run_cli(*arguments)

    assert failure.exit_code == 1
    assert failure.out == ""
    assert expected_message in failure.err


def test_malformed_config_file_fails_with_one_line(
    reporting_config: ReportingConfigFixture,
    run_cli: RunCli,
) -> None:
    reporting_config()
    config_file.config_path().write_text('{"app": {"minute-round-to": "abc"}}', encoding="utf-8")

    failure = run_cli("config", "list")

    assert failure.exit_code == 1
    assert failure.out == ""
    assert failure.err.startswith("Error: Config file ")
    assert "app.minute-round-to: " in failure.err
    assert failure.err.count("\n") == 2
