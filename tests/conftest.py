import hashlib
import json
import os
import random
from collections.abc import Generator
from pathlib import Path
from typing import Protocol

import pytest
from sqlalchemy.orm import Session

from reporting import config
from reporting.config import config_file
from reporting.database import db_connection
from reporting.database.models import Base
from tests import factories

FAKER_SEED_VARIABLE = "REPORTING_TEST_FAKER_SEED"

pytest_plugins = [
    "tests.fixtures.cli",
    "tests.fixtures.portal",
]

_session_faker_seed = int(os.environ.get(FAKER_SEED_VARIABLE) or random.randrange(1000000))


class ReportingConfigFixture(Protocol):
    def __call__(self, config_data: dict | None = None) -> None: ...


@pytest.fixture(autouse=True)  # autouse for factory usage in any moment
def database_session() -> Generator[Session]:
    config.app.sqlite_database_path = ":memory:"
    db_connection.reconnect()

    if db_connection.session_factory is None or db_connection.engine is None:
        raise RuntimeError("Database is not connected")

    session = db_connection.session_factory()
    factories.set_session(session)

    yield session

    session.rollback()
    session.close()
    factories.set_session(None)
    Base.metadata.drop_all(bind=db_connection.engine)
    db_connection.engine.dispose()


@pytest.fixture(autouse=True)
def faker_seed(request: pytest.FixtureRequest) -> int:
    digest = hashlib.sha256(f"{_session_faker_seed}:{request.node.nodeid}".encode()).digest()
    return int.from_bytes(digest[:4], "big")


def pytest_report_header() -> str:
    return f"faker seed: {_session_faker_seed} (set {FAKER_SEED_VARIABLE} to reproduce)"


@pytest.fixture(scope="session")
def reporting_base_dir(test_environment: None) -> Path:
    return config_file.config_path().parent


@pytest.fixture
def reporting_config(
    reporting_base_dir: Path,
) -> Generator[ReportingConfigFixture]:
    config_path = config_file.config_path()
    config_default: dict = {
        "app": {
            "hour-report-path": "",
            "minute-round-to": 0,
            "omit-task": [],
            "sqlite-database-path": ":memory:",
        },
        "dictionary": {
            "task": {},
            "type": {},
            "project": {},
        },
    }

    def config_save(config_data: dict | None = None) -> None:
        if not config_data:
            config_data = {}

        config_union: dict = {}

        for section_name in set(config_default) | set(config_data):
            default_section = config_default.get(section_name, {})
            given_section = config_data.get(section_name, {})

            if isinstance(default_section, dict) and isinstance(given_section, dict):
                config_union[section_name] = dict(default_section, **given_section)
            else:
                config_union[section_name] = given_section

        config_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.write_text(json.dumps(config_union), encoding="utf-8")
        config.reload()

    yield config_save

    os.remove(config_path)
    config.reload()


@pytest.fixture(scope="session", autouse=True)
def test_environment(tmp_path_factory: pytest.TempPathFactory) -> Generator[None]:
    with pytest.MonkeyPatch.context() as patch:
        patch.setenv("COLUMNS", "100")
        patch.setenv("NO_COLOR", "1")
        patch.setenv("TERM", "dumb")
        patch.setenv("XDG_CONFIG_HOME", str(tmp_path_factory.mktemp("config")))
        patch.delenv("FORCE_COLOR", raising=False)
        yield
