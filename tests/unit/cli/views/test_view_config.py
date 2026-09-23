import pathlib

from reporting.cli.views import view_config
from reporting.config.models import RootConfig
from tests.assertions import cli_output

_CONFIG_PATH = pathlib.Path("/home/someone/.config/reporting/config.json")


def test_marks_a_missing_config_file_in_the_location_line() -> None:
    output = cli_output.render(view_config.render(_CONFIG_PATH, False, RootConfig()))

    assert f"Config file: {_CONFIG_PATH} (does not exist, every value is a default)" in cli_output.flat_text(output)


def test_marks_a_saved_value_as_saved() -> None:
    root = RootConfig.model_validate({"app": {"minute-round-to": 25}})

    output = cli_output.flat_text(cli_output.render(view_config.render_saved_value(root, "app.minute-round-to")))

    assert "app.minute-round-to 25" in output
    assert "saved" in output


def test_renders_a_group_setting_without_entries_as_empty() -> None:
    output = cli_output.render(view_config.render_value(RootConfig(), "dictionary.task"))

    assert "dictionary.task (empty)" in cli_output.flat_text(output)


def test_renders_a_list_setting_without_items_as_empty() -> None:
    output = cli_output.render(view_config.render_value(RootConfig(), "app.omit-task"))

    assert "app.omit-task (empty)" in cli_output.flat_text(output)


def test_renders_a_scalar_setting_with_its_value() -> None:
    root = RootConfig.model_validate({"jira": {"server": "https://jira.example.com"}})

    output = cli_output.render(view_config.render_value(root, "jira.server"))

    assert "jira.server https://jira.example.com" in cli_output.flat_text(output)


def test_renders_a_setting_without_a_value_as_empty() -> None:
    output = cli_output.render(view_config.render_value(RootConfig(), "jira.password"))

    assert "jira.password (empty)" in cli_output.flat_text(output)


def test_renders_each_section_with_its_key_hint() -> None:
    output = cli_output.flat_text(cli_output.render(view_config.render(_CONFIG_PATH, True, RootConfig())))

    assert "Jira jira.*" in output
    assert "QATestLab Portal qatestlab-portal.*" in output


def test_renders_every_setting_of_a_section() -> None:
    root = RootConfig.model_validate({"jira": {"login": "someone", "server": "https://jira.example.com"}})

    output = cli_output.flat_text(cli_output.render(view_config.render_value(root, "jira")))

    assert "jira.login someone" in output
    assert "jira.server https://jira.example.com" in output
    assert "jira.password (empty)" in output


def test_renders_the_entries_of_a_group_setting() -> None:
    root = RootConfig.model_validate({"dictionary": {"task": {"b": "break", "l": "lunch"}}})

    output = cli_output.flat_text(cli_output.render(view_config.render_value(root, "dictionary.task")))

    assert "b break" in output
    assert "l lunch" in output


def test_renders_the_items_of_a_list_setting() -> None:
    root = RootConfig.model_validate({"app": {"omit-task": ["lunch", "break"]}})

    output = cli_output.flat_text(cli_output.render(view_config.render_value(root, "app.omit-task")))

    assert "lunch" in output
    assert "break" in output


def test_shows_the_config_file_path_when_the_file_exists() -> None:
    output = cli_output.flat_text(cli_output.render(view_config.render(_CONFIG_PATH, True, RootConfig())))

    assert f"Config file: {_CONFIG_PATH}" in output
    assert "does not exist" not in output
