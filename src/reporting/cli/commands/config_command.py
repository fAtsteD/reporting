from typing import Any

import typer
from pydantic import ValidationError

from reporting import config
from reporting.cli import output
from reporting.cli.views import view_config
from reporting.config import config_access, config_file, validation_message
from reporting.config.exceptions import ConfigError
from reporting.config.models import RootConfig

app = typer.Typer(help="View and change configuration")


@app.command("get", help="Print the value of one setting")
def get(
    key: str = typer.Argument(..., help="Configuration key, for example jira.server"),
) -> None:
    output.print_result(view_config.render_value(config.current, key))


@app.command("list", help="Print the config file location and every setting with its value")
def list_values() -> None:
    config_file_path = config_file.config_path()

    output.print_result(view_config.render(config_file_path, config_file_path.is_file(), config.current))


@app.command(
    "set",
    help=(
        "Set a value. Address an entry of a dictionary setting by its name, for example "
        "dictionary.task.l. For a list setting the value is added as one more item"
    ),
)
def set_value(
    key: str = typer.Argument(..., help="Configuration key, for example jira.server"),
    value: str = typer.Argument(..., help="Value to set, or one item to add to a list"),
) -> None:
    data = config_file.read_data()
    config_access.set_value(data, key, value)
    _save(data, key)


@app.command(
    "unset",
    help=("Reset a setting to its default. For a list setting pass a value to remove only that item"),
)
def unset_value(
    key: str = typer.Argument(..., help="Configuration key, for example jira.server"),
    value: str = typer.Argument("", help="One item to remove from a list"),
) -> None:
    data = config_file.read_data()
    config_access.unset_value(data, key, value)
    _save(data, key)


def _save(data: dict[str, Any], key: str) -> None:
    try:
        root = RootConfig.model_validate(data)
    except ValidationError as error:
        raise ConfigError(f"Value is not valid for {key}:\n{validation_message.describe(error)}") from error

    config_file.save(root)
    config.reload()
    output.print_result(view_config.render_saved_value(root, key))
