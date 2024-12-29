import datetime

import factory

from reporting import database
from reporting.models import Kind, Project, Report, Task

# Use if for relational factories
_current_module = "tests.factories"


class BaseFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        abstract = True
        sqlalchemy_session_persistence = "commit"

        @staticmethod
        def sqlalchemy_session_factory():
            return database.session


class KindFactory(BaseFactory):
    class Meta:
        model = Kind

    alias = factory.Sequence(lambda index: f"kind_alias_{index}")
    created_at = factory.Faker("date_time")
    id = factory.Sequence(lambda index: index + 100)
    name = factory.Faker("sentence", nb_words=3, variable_nb_words=True)
    tasks = factory.RelatedFactoryList(
        factory=f"{_current_module}.TaskFactory",
        factory_related_name="kind",
        kinds_id=factory.SelfAttribute("..id"),
    )
    updated_at = factory.Faker("date_time")


class ProjectFactory(BaseFactory):
    class Meta:
        model = Project

    alias = factory.Sequence(lambda index: f"project_alias_{index}")
    created_at = factory.Faker("date_time")
    id = factory.Sequence(lambda index: index + 100)
    name = factory.Faker("sentence", nb_words=3, variable_nb_words=True)
    tasks = factory.RelatedFactoryList(
        factory=f"{_current_module}.TaskFactory",
        factory_related_name="project",
        projects_id=factory.SelfAttribute("..id"),
    )
    updated_at = factory.Faker("date_time")


class ReportFactory(BaseFactory):
    class Meta:
        model = Report

    created_at = factory.Faker("date_time")
    date = factory.Sequence(lambda index: datetime.datetime.now() - datetime.timedelta(days=index + 100))
    id = factory.Sequence(lambda index: index + 100)
    tasks = factory.RelatedFactoryList(
        factory=f"{_current_module}.TaskFactory",
        factory_related_name="report",
        reports_id=factory.SelfAttribute("..id"),
        size=6,
    )
    updated_at = factory.Faker("date_time")


class TaskFactory(BaseFactory):
    class Meta:
        model = Task

    created_at = factory.Faker("date_time")
    id = factory.Sequence(lambda index: index + 100)
    kind = factory.SubFactory(
        factory=f"{_current_module}.KindFactory",
        tasks=[],
    )
    kinds_id = factory.SelfAttribute("kind.id")
    logged_seconds = factory.Faker("random_int", min=60, max=60000)
    project = factory.SubFactory(
        factory=f"{_current_module}.ProjectFactory",
        tasks=[],
    )
    projects_id = factory.SelfAttribute("project.id")
    report = factory.SubFactory(
        factory=f"{_current_module}.ReportFactory",
        tasks=[],
    )
    reports_id = factory.SelfAttribute("report.id")
    summary = factory.Faker("sentence", nb_words=10, variable_nb_words=True)
    updated_at = factory.Faker("date_time")
