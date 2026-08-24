import json
import os
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from reporting.config.exceptions import ConfigError
from reporting.config.models import RootConfig

CONFIG_DIR_NAME = "reporting"
CONFIG_FILE_NAME = "config.json"


def config_path() -> Path:
    config_home = os.environ.get("XDG_CONFIG_HOME")
    base_dir = Path(config_home) if config_home else Path.home() / ".config"

    return base_dir / CONFIG_DIR_NAME / CONFIG_FILE_NAME


def load() -> RootConfig:
    try:
        return RootConfig.model_validate(read_data())
    except ValidationError as error:
        raise ConfigError(f"Config file {config_path()} is not valid:\n{error}") from error


def read_data() -> dict[str, Any]:
    file_path = config_path()

    if not file_path.is_file():
        return {}

    try:
        data = json.loads(file_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ConfigError(f"Config file {file_path} is not valid JSON: {error}") from error

    if not isinstance(data, dict):
        raise ConfigError(f"Config file {file_path} has to contain a JSON object")

    return data


def write_data(data: dict[str, Any]) -> None:
    file_path = config_path()
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(json.dumps(data, ensure_ascii=False, indent=4, sort_keys=True) + "\n", encoding="utf-8")
