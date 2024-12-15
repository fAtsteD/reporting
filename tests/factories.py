import factory

from reporting.models.kind import Kind
from reporting.models.project import Project
from reporting.models.report import Report
from reporting.models.task import Task

# Use if for relational factories
_current_module = "tests.factories"


class BaseFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        abstract = True
        sqlalchemy_session_persistence = "commit"

        @staticmethod
        def sqlalchemy_session_factory():
            from reporting.config_app import config

            return config.sqlite_session


class KindFactory(BaseFactory):
    class Meta:
        model = Kind

    alias = factory.Faker("word")
    created_at = factory.Faker("date_time")
    id = factory.Faker("random_int", min=1, max=10000)
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

    alias = factory.Faker("word")
    created_at = factory.Faker("date_time")
    id = factory.Faker("random_int", min=1, max=10000)
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
    date = factory.Faker("date_time")
    id = factory.Faker("random_int", min=1, max=10000)
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
    id = factory.Faker("random_int", min=1, max=10000)
    kind = factory.RelatedFactory(
        factory=f"{_current_module}.KindFactory",
        factory_related_name="tasks",
        id=factory.SelfAttribute("..kinds_id"),
    )
    kinds_id = factory.Faker("random_int", min=1, max=10000)
    logged_seconds = factory.Faker("random_int", min=60, max=60000)
    project = factory.RelatedFactory(
        factory=f"{_current_module}.ProjectFactory",
        factory_related_name="tasks",
        id=factory.SelfAttribute("..projects_id"),
    )
    projects_id = factory.Faker("random_int", min=1, max=10000)
    report = factory.RelatedFactory(
        factory=f"{_current_module}.ReportFactory",
        factory_related_name="tasks",
        id=factory.SelfAttribute("..reports_id"),
    )
    reports_id = factory.Faker("random_int", min=1, max=10000)
    summary = factory.Faker("sentence", nb_words=10, variable_nb_words=True)
    updated_at = factory.Faker("date_time")
