import datetime
from typing import Any

import factory
from sqlalchemy.orm.session import Session

from reporting.database.models import Base, Kind, Project, Report, Task

_FIRST_REPORT_DATE = datetime.date(2020, 1, 1)

db_session: Session | None = None


class BaseFactory[FactoryModelType: Base](factory.alchemy.SQLAlchemyModelFactory):
    class Meta:  # pyright: ignore
        abstract = True
        sqlalchemy_session_persistence = "commit"

        @classmethod
        def sqlalchemy_session_factory(cls) -> Session:
            if not db_session:
                raise RuntimeError(
                    "Database session is not set. Please set the 'db_session' variable before using the factory."
                )

            return db_session

    @classmethod
    def build(cls, **kwargs: Any) -> FactoryModelType:
        return super().build(**kwargs)

    @classmethod
    def build_batch(cls, size: int, **kwargs: Any) -> list[FactoryModelType]:
        return super().build_batch(size, **kwargs)

    @classmethod
    def create(cls, **kwargs: Any) -> FactoryModelType:
        return super().create(**kwargs)

    @classmethod
    def create_batch(cls, size: int, **kwargs: Any) -> list[FactoryModelType]:
        return super().create_batch(size, **kwargs)


class KindFactory(BaseFactory[Kind]):
    class Meta:  # pyright: ignore
        model = Kind

    alias = factory.declarations.Sequence(lambda index: f"kind_alias_{index}")
    name = factory.faker.Faker("sentence", nb_words=3, variable_nb_words=True)


class ProjectFactory(BaseFactory[Project]):
    class Meta:  # pyright: ignore
        model = Project

    alias = factory.declarations.Sequence(lambda index: f"project_alias_{index}")
    name = factory.faker.Faker("sentence", nb_words=3, variable_nb_words=True)


class ReportFactory(BaseFactory[Report]):
    class Meta:  # pyright: ignore
        model = Report

    date = factory.declarations.Sequence(lambda index: _FIRST_REPORT_DATE + datetime.timedelta(days=index))


class TaskFactory(BaseFactory[Task]):
    class Meta:  # pyright: ignore
        model = Task

    kind = factory.declarations.SubFactory(f"{__name__}.KindFactory")
    logged_seconds = factory.faker.Faker("random_int", min=60, max=60000)
    project = factory.declarations.SubFactory(f"{__name__}.ProjectFactory")
    report = factory.declarations.SubFactory(f"{__name__}.ReportFactory")
    summary = factory.faker.Faker("sentence", nb_words=10, variable_nb_words=True)
