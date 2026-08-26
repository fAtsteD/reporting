import typer

from reporting.cli import output
from reporting.cli.views import view_project
from reporting.database import db_connection
from reporting.services.project import project_service

app = typer.Typer(help="Manage projects")


@app.command("add")
def add(
    alias: str = typer.Argument(..., help="Project alias (unique)"),
    name: str = typer.Argument(..., help="Project name"),
) -> None:
    with db_connection.session_scope() as session:
        output.print_result(view_project.render(project_service.save_project(session, alias, name)))


@app.command("list")
def list_projects() -> None:
    with db_connection.session_scope() as session:
        output.print_result(view_project.render(project_service.list_projects(session)))
