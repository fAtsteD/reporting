import contextlib
import datetime
import json
from collections.abc import Generator
from pathlib import Path
from typing import Protocol

import faker
import pytest
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session

from reporting.config_app.class_config import Config
from reporting.models import Base
from reporting.models.kind import Kind
from reporting.models.project import Project
from reporting.models.report import Report
from reporting.models.task import Task


class KindFixture(Protocol):
    def __call__(
        self,
        alias: str | None = None,
        name: str | None = None,
    ) -> Kind: ...


class ProjectFixture(Protocol):
    def __call__(
        self,
        alias: str | None = None,
        name: str | None = None,
    ) -> Project: ...


class ReportFixture(Protocol):
    def __call__(
        self,
        date: datetime.date | None = None,
    ) -> Report: ...


class ReportingConfigFixture(Protocol):
    def __call__(self, config: dict = {}) -> None: ...


class TaskFixture(Protocol):
    def __call__(
        self,
        kind: str | Kind | None = None,
        logged_seconds: int | None = None,
        project: str | Project | None = None,
        report: Report | None = None,
        summary: str | None = None,
    ) -> Task: ...


@pytest.fixture
def add_task(
    database_session: Session,
    get_kind: KindFixture,
    get_project: ProjectFixture,
    get_report: ReportFixture,
    faker: faker.Faker,
) -> TaskFixture:
    kind_default = Kind(alias="tk", name="Test Kind")
    project_default = Project(alias="tp", name="Test Project")
    database_session.add_all([kind_default, project_default])
    database_session.commit()
    report_default = get_report()

    def generate_task(
        kind: str | Kind | None = None,
        logged_seconds: int | None = None,
        project: str | Project | None = None,
        report: Report | None = None,
        summary: str | None = None,
    ) -> Task:
        project_obj = project_default
        kind_obj = kind_default

        if isinstance(project, Project):
            database_session.add(project)
            project_obj = project
        else:
            project_obj = get_project(name=project)

        if isinstance(kind, Kind):
            database_session.add(kind)
            kind_obj = kind
        else:
            kind_obj = get_kind(name=kind)

        task = Task(
            kind=kind_obj,
            logged_seconds=(
                logged_seconds
                if isinstance(logged_seconds, int) and logged_seconds >= 0
                else faker.random_int(0, 2 * 60 * 60, 60)
            ),
            project=project_obj,
            report=report if report else report_default,
            summary=summary if summary else faker.sentence(),
        )
        database_session.add(task)
        database_session.commit()
        return task

    return generate_task


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


@pytest.fixture
def get_kind(
    database_session: Session,
    faker: faker.Faker,
) -> KindFixture:
    def generate_kind(
        alias: str | None = None,
        name: str | None = None,
    ) -> Kind:
        kind = database_session.query(Kind).filter(Kind.alias == alias).first()

        if not kind:
            kind = Kind(
                alias=alias if alias else faker.word().lower(),
                name=name if name else faker.name(),
            )

        kind.name = name if name else kind.name
        database_session.add(kind)
        database_session.commit()
        return kind

    return generate_kind


@pytest.fixture
def get_project(
    database_session: Session,
    faker: faker.Faker,
) -> ProjectFixture:
    def generate_project(
        alias: str | None = None,
        name: str | None = None,
    ) -> Project:
        project = database_session.query(Project).filter(Project.alias == alias).first()

        if not project:
            project = Project(
                alias=alias if alias else faker.word().lower(),
                name=name if name else faker.name(),
            )

        project.name = name if name else project.name
        database_session.add(project)
        database_session.commit()
        return project

    return generate_project


@pytest.fixture
def get_report(
    database_session: Session,
    faker: faker.Faker,
) -> ReportFixture:
    report_default = Report(date=faker.date_object())
    database_session.add(report_default)
    database_session.commit()

    def generate_report(
        date: datetime.date | None = None,
    ) -> Report:
        if date:
            report = database_session.query(Report).filter(Report.date == date).first()

            if not report:
                report = Report(date=date)
                database_session.add(report)
                database_session.commit()

            return report
        return report_default

    return generate_report


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
