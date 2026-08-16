import sqlalchemy as sa
import typer
from sqlalchemy.orm import Session

from reporting import config
from reporting.database import db_connection
from reporting.database.models import Project

app = typer.Typer(help="Manage projects")


@app.command("add")
def add(
    alias: str = typer.Argument(..., help="Project alias (unique)"),
    name: str = typer.Argument(..., help="Project name"),
) -> None:
    """Add or update project."""
    config.load_config()

    with db_connection.session_scope() as session:
        project: Project | None = session.scalars(sa.select(Project).where(Project.alias == alias)).first()

        if project is None:
            project = Project(alias=alias, name=name)
            session.add(project)
            session.flush()
        else:
            project.name = name

        _list_projects(session)


@app.command("list")
def list_projects() -> None:
    """Print all projects."""
    config.load_config()

    with db_connection.session_scope() as session:
        _list_projects(session)


def _list_projects(session: Session) -> None:
    projects = session.scalars(sa.select(Project).order_by(Project.name)).all()
    print("Projects:")

    for project in projects:
        print(project)
