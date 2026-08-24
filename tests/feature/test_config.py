import json

import pytest

from reporting import cli, config
from reporting.config import config_access, config_file
from tests.conftest import ReportingConfigFixture


def test_list_shows_config_file_path(
    capsys: pytest.CaptureFixture,
    reporting_config: ReportingConfigFixture,
) -> None:
    config_path = config_file.config_path()

    cli.main(["config", "list"])
    assert capsys.readouterr().out.startswith(
        f"Config file: {config_path} (does not exist, every value is a default)\n"
    )

    reporting_config()

    cli.main(["config", "list"])
    assert capsys.readouterr().out.startswith(f"Config file: {config_path}\n")


def test_list_shows_every_setting_with_description(
    capsys: pytest.CaptureFixture,
    reporting_config: ReportingConfigFixture,
) -> None:
    reporting_config()

    cli.main(["config", "list"])

    output = capsys.readouterr().out

    for key, _, description in config_access.iterate_values(config.current):
        assert key in output
        assert description, f"{key} does not have a description"
        assert description in output


@pytest.mark.parametrize(
    "key, value, expected",
    [
        pytest.param("app.timezone", "Europe/Kyiv", "Europe/Kyiv", id="text"),
        pytest.param("app.minute-round-to", "25", "25", id="number"),
        pytest.param("dictionary.task.l", "lunch", "lunch", id="dictionary entry"),
    ],
)
def test_set_and_get_value(
    capsys: pytest.CaptureFixture,
    expected: str,
    key: str,
    reporting_config: ReportingConfigFixture,
    value: str,
) -> None:
    reporting_config()

    cli.main(["config", "set", key, value])
    assert capsys.readouterr().out == f"{key} = {expected}\n"

    cli.main(["config", "get", key])
    assert capsys.readouterr().out == f"{expected}\n"


def test_set_saves_value_in_the_config_file(reporting_config: ReportingConfigFixture) -> None:
    reporting_config()

    cli.main(["config", "set", "app.minute-round-to", "25"])

    saved = json.loads(config_file.config_path().read_text(encoding="utf-8"))
    assert saved["app"]["minute-round-to"] == 25


@pytest.mark.parametrize(
    "key, expected",
    [
        pytest.param("jira.password", "", id="text returns to default"),
        pytest.param("dictionary.task.l", "null", id="dictionary entry is removed"),
    ],
)
def test_unset_returns_value_to_default(
    capsys: pytest.CaptureFixture,
    expected: str,
    key: str,
    reporting_config: ReportingConfigFixture,
) -> None:
    reporting_config(
        {
            "dictionary": {"task": {"l": "lunch"}},
            "jira": {"password": "secret"},
        }
    )

    cli.main(["config", "unset", key])
    capsys.readouterr()
    cli.main(["config", "get", key])

    assert capsys.readouterr().out == f"{expected}\n"


def test_set_and_unset_list_items(
    capsys: pytest.CaptureFixture,
    reporting_config: ReportingConfigFixture,
) -> None:
    reporting_config()

    cli.main(["config", "set", "app.omit-task", "lunch"])
    assert capsys.readouterr().out == 'app.omit-task = ["lunch"]\n'

    cli.main(["config", "set", "app.omit-task", "break"])
    assert capsys.readouterr().out == 'app.omit-task = ["lunch", "break"]\n'

    cli.main(["config", "set", "app.omit-task", "lunch"])
    assert capsys.readouterr().out == 'app.omit-task = ["lunch", "break"]\n'

    cli.main(["config", "unset", "app.omit-task", "lunch"])
    assert capsys.readouterr().out == 'app.omit-task = ["break"]\n'

    cli.main(["config", "unset", "app.omit-task"])
    assert capsys.readouterr().out == "app.omit-task = []\n"


def test_set_adds_json_array_as_one_list_item(
    capsys: pytest.CaptureFixture,
    reporting_config: ReportingConfigFixture,
) -> None:
    reporting_config()

    cli.main(["config", "set", "app.omit-task", '["a","b"]'])

    assert capsys.readouterr().out == 'app.omit-task = ["[\\"a\\",\\"b\\"]"]\n'


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
    capsys: pytest.CaptureFixture,
    expected_message: str,
    reporting_config: ReportingConfigFixture,
) -> None:
    reporting_config({"app": {"omit-task": ["lunch"]}})

    with pytest.raises(SystemExit) as exit_info:
        cli.main(arguments)

    assert exit_info.value.code == 1
    assert expected_message in capsys.readouterr().out
