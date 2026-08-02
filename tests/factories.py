import datetime
from typing import TypeVar

import factory

from reporting import database
from reporting.models import Base, Kind, Project, Report, Task

FactoryModelType = TypeVar("FactoryModelType")


class BaseFactory[FactoryModelType: Base](factory.alchemy.SQLAlchemyModelFactory):
    class Meta:  # pyright: ignore
        abstract = True
        sqlalchemy_session_persistence = "commit"

        @staticmethod
        def sqlalchemy_session_factory():
            return database.session

    @classmethod
    def create(cls, **kwargs) -> FactoryModelType:
        # Redefine for type hinting, because alchemy factory does not support generic like base Factory. Remove when alchemy factory will be generic
        return super().create(**kwargs)

    @classmethod
    def create_batch(cls, size: int, **kwargs) -> list[FactoryModelType]:
        # Redefine for type hinting, because alchemy factory does not support generic like base Factory. Remove when alchemy factory will be generic
        return super().create_batch(size, **kwargs)

    @classmethod
    def build(cls, **kwargs) -> FactoryModelType:
        # Redefine for type hinting, because alchemy factory does not support generic like base Factory. Remove when alchemy factory will be generic
        return super().build(**kwargs)

    @classmethod
    def build_batch(cls, size: int, **kwargs) -> list[FactoryModelType]:
        # Redefine for type hinting, because alchemy factory does not support generic like base Factory. Remove when alchemy factory will be generic
        return super().build_batch(size, **kwargs)


class KindFactory(BaseFactory[Kind]):
    class Meta:  # pyright: ignore
        model = Kind

    alias = factory.declarations.Sequence(lambda index: f"kind_alias_{index}")
    created_at = factory.faker.Faker("date_time")
    id = factory.declarations.Sequence(lambda index: index + 100)
    name = factory.faker.Faker("sentence", nb_words=3, variable_nb_words=True)
    tasks = factory.declarations.RelatedFactoryList(
        factory=f"{__name__}.TaskFactory",
        factory_related_name="kind",
        kinds_id=factory.declarations.SelfAttribute("..id"),
    )
    updated_at = factory.faker.Faker("date_time")


class ProjectFactory(BaseFactory[Project]):
    class Meta:  # pyright: ignore
        model = Project

    alias = factory.declarations.Sequence(lambda index: f"project_alias_{index}")
    created_at = factory.faker.Faker("date_time")
    id = factory.declarations.Sequence(lambda index: index + 100)
    name = factory.faker.Faker("sentence", nb_words=3, variable_nb_words=True)
    tasks = factory.declarations.RelatedFactoryList(
        factory=f"{__name__}.TaskFactory",
        factory_related_name="project",
        projects_id=factory.declarations.SelfAttribute("..id"),
    )
    updated_at = factory.faker.Faker("date_time")


class ReportFactory(BaseFactory[Report]):
    class Meta:  # pyright: ignore
        model = Report

    created_at = factory.faker.Faker("date_time")
    date = factory.declarations.Sequence(
        lambda index: datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=index + 100)
    )
    id = factory.declarations.Sequence(lambda index: index + 100)
    tasks = factory.declarations.RelatedFactoryList(
        factory=f"{__name__}.TaskFactory",
        factory_related_name="report",
        reports_id=factory.declarations.SelfAttribute("..id"),
        size=6,
    )
    updated_at = factory.faker.Faker("date_time")


class TaskFactory(BaseFactory[Task]):
    class Meta:  # pyright: ignore
        model = Task

    created_at = factory.faker.Faker("date_time")
    id = factory.declarations.Sequence(lambda index: index + 100)
    kind = factory.declarations.SubFactory(
        factory=f"{__name__}.KindFactory",
        tasks=[],
    )
    kinds_id = factory.declarations.SelfAttribute("kind.id")
    logged_seconds = factory.faker.Faker("random_int", min=60, max=60000)
    project = factory.declarations.SubFactory(
        factory=f"{__name__}.ProjectFactory",
        tasks=[],
    )
    projects_id = factory.declarations.SelfAttribute("project.id")
    report = factory.declarations.SubFactory(
        factory=f"{__name__}.ReportFactory",
        tasks=[],
    )
    reports_id = factory.declarations.SelfAttribute("report.id")
    summary = factory.faker.Faker("sentence", nb_words=10, variable_nb_words=True)
    updated_at = factory.faker.Faker("date_time")
