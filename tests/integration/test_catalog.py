from sqlalchemy.orm import Session

from reporting.services.kind import kind_service
from reporting.services.project import project_service
from tests.factories.database import KindFactory, ProjectFactory


def test_lists_kinds_ordered_by_name(database_session: Session) -> None:
    KindFactory.create(alias="k3", name="Gamma")
    KindFactory.create(alias="k1", name="Alpha")
    KindFactory.create(alias="k2", name="Beta")

    assert [kind.name for kind in kind_service.list_kinds(database_session)] == ["Alpha", "Beta", "Gamma"]


def test_lists_no_kind_when_none_is_saved(database_session: Session) -> None:
    assert list(kind_service.list_kinds(database_session)) == []


def test_lists_no_project_when_none_is_saved(database_session: Session) -> None:
    assert list(project_service.list_projects(database_session)) == []


def test_lists_projects_ordered_by_name(database_session: Session) -> None:
    ProjectFactory.create(alias="p3", name="Gamma")
    ProjectFactory.create(alias="p1", name="Alpha")
    ProjectFactory.create(alias="p2", name="Beta")

    assert [project.name for project in project_service.list_projects(database_session)] == ["Alpha", "Beta", "Gamma"]


def test_renames_a_kind_with_a_known_alias(database_session: Session) -> None:
    KindFactory.create(alias="dev", name="Old Name")

    kind_service.save_kind(database_session, "dev", "New Name")

    assert [(kind.alias, kind.name) for kind in kind_service.list_kinds(database_session)] == [("dev", "New Name")]


def test_renames_a_project_with_a_known_alias(database_session: Session) -> None:
    ProjectFactory.create(alias="mp", name="Old Name")

    project_service.save_project(database_session, "mp", "New Name")

    assert [(project.alias, project.name) for project in project_service.list_projects(database_session)] == [
        ("mp", "New Name")
    ]


def test_saves_a_new_kind(database_session: Session) -> None:
    kind_service.save_kind(database_session, "dev", "Develop")

    assert [(kind.alias, kind.name) for kind in kind_service.list_kinds(database_session)] == [("dev", "Develop")]


def test_saves_a_new_project(database_session: Session) -> None:
    project_service.save_project(database_session, "mp", "My Project")

    assert [(project.alias, project.name) for project in project_service.list_projects(database_session)] == [
        ("mp", "My Project")
    ]
