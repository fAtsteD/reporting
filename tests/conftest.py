import contextlib
import json
from collections.abc import Generator
from pathlib import Path
from typing import Protocol

import pytest
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session

from reporting.config_app.class_config import Config
from reporting.models import Base


class ReportingConfigFixture(Protocol):
    def __call__(self, config: dict = {}) -> None: ...


@pytest.fixture(scope="session")
def database_path() -> str:
    return ":memory:"


@pytest.fixture(scope="session")
def database_engine(database_path: str) -> Generator[Engine]:
    engine = create_engine(
        "sqlite:///" + database_path,
        echo=False,
    )
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


@pytest.fixture
def database_session(
    database_engine: Engine,
    monkeypatch: pytest.MonkeyPatch,
) -> Generator[Session]:
    session = Session(bind=database_engine)
    monkeypatch.setattr(Config, "sqlite_session", session)

    yield session

    session.rollback()
    session.close()

    with contextlib.closing(database_engine.connect()) as connection:
        transaction = connection.begin()
        for table in reversed(Base.metadata.sorted_tables):
            connection.execute(table.delete())
        transaction.commit()


@pytest.fixture(scope="session")
def reporting_base_dir(tmp_path_factory: pytest.TempPathFactory) -> Path:
    dir = tmp_path_factory.mktemp("reporting")
    Config.program_dir = dir.absolute()
    return dir


@pytest.fixture
def reporting_config(
    database_path: str,
    reporting_base_dir: Path,
) -> ReportingConfigFixture:
    config_path = reporting_base_dir / "config.json"
    config_default = {
        "hour-report-path": "",
        "sqlite-database-path": database_path,
        "omit-task": [],
        "minute-round-to": 0,
        "dictionary": {
            "task": {},
            "type": {},
            "project": {},
        },
    }

    def config_save(config: dict = {}) -> None:
        config_union = dict(config_default, **config)
        with config_path.open("w", encoding="utf-8") as config_file:
            json.dump(config_union, config_file)

    return config_save
