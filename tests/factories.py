import datetime

import factory

from reporting import database
from reporting.models import Kind, Project, Report, Task

# Use if for relational factories
_current_module = "tests.factories"


class BaseFactory(factory.alchemy.SQLAlchemyModelFactory):

    class Meta(factory.alchemy.SQLAlchemyModelFactory.Meta):
        abstract = True
        sqlalchemy_session_persistence = "commit"

        @staticmethod
        def sqlalchemy_session_factory():
            return database.session


class KindFactory(BaseFactory):

    class Meta(BaseFactory.Meta):
        model = Kind

    alias = factory.declarations.Sequence(lambda index: f"kind_alias_{index}")
    created_at = factory.faker.Faker("date_time")
    id = factory.declarations.Sequence(lambda index: index + 100)
    name = factory.faker.Faker("sentence", nb_words=3, variable_nb_words=True)
    tasks = factory.declarations.RelatedFactoryList(
        factory=f"{_current_module}.TaskFactory",
        factory_related_name="kind",
        kinds_id=factory.declarations.SelfAttribute("..id"),
    )
    updated_at = factory.faker.Faker("date_time")


class ProjectFactory(BaseFactory):

    class Meta(BaseFactory.Meta):
        model = Project

    alias = factory.declarations.Sequence(lambda index: f"project_alias_{index}")
    created_at = factory.faker.Faker("date_time")
    id = factory.declarations.Sequence(lambda index: index + 100)
    name = factory.faker.Faker("sentence", nb_words=3, variable_nb_words=True)
    tasks = factory.declarations.RelatedFactoryList(
        factory=f"{_current_module}.TaskFactory",
        factory_related_name="project",
        projects_id=factory.declarations.SelfAttribute("..id"),
    )
    updated_at = factory.faker.Faker("date_time")


class ReportFactory(BaseFactory):

    class Meta(BaseFactory.Meta):
        model = Report

    created_at = factory.faker.Faker("date_time")
    date = factory.declarations.Sequence(lambda index: datetime.datetime.now() - datetime.timedelta(days=index + 100))
    id = factory.declarations.Sequence(lambda index: index + 100)
    tasks = factory.declarations.RelatedFactoryList(
        factory=f"{_current_module}.TaskFactory",
        factory_related_name="report",
        reports_id=factory.declarations.SelfAttribute("..id"),
        size=6,
    )
    updated_at = factory.faker.Faker("date_time")


class TaskFactory(BaseFactory):

    class Meta(BaseFactory.Meta):
        model = Task

    created_at = factory.faker.Faker("date_time")
    id = factory.declarations.Sequence(lambda index: index + 100)
    kind = factory.declarations.SubFactory(
        factory=f"{_current_module}.KindFactory",
        tasks=[],
    )
    kinds_id = factory.declarations.SelfAttribute("kind.id")
    logged_seconds = factory.faker.Faker("random_int", min=60, max=60000)
    project = factory.declarations.SubFactory(
        factory=f"{_current_module}.ProjectFactory",
        tasks=[],
    )
    projects_id = factory.declarations.SelfAttribute("project.id")
    report = factory.declarations.SubFactory(
        factory=f"{_current_module}.ReportFactory",
        tasks=[],
    )
    reports_id = factory.declarations.SelfAttribute("report.id")
    summary = factory.faker.Faker("sentence", nb_words=10, variable_nb_words=True)
    updated_at = factory.faker.Faker("date_time")
