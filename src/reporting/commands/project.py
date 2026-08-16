import typer

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
    project: Project | None = db_connection.session.query(Project).filter(Project.alias == alias).first()

    if project is None:
        project = Project(alias=alias, name=name)
        db_connection.session.add(project)
    else:
        project.name = name

    db_connection.session.commit()
    list_projects()


@app.command("list")
def list_projects() -> None:
    """Print all projects."""
    projects = db_connection.session.query(Project).order_by(Project.name).all()
    print("Projects:")

    for project in projects:
        print(project)
