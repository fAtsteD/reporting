import typer

from reporting.cli import views
from reporting.database import db_connection
from reporting.services.kind import kind_service

app = typer.Typer(help="Manage kinds")


@app.command("add")
def add(
    alias: str = typer.Argument(..., help="Kind alias (unique)"),
    name: str = typer.Argument(..., help="Kind name"),
) -> None:
    with db_connection.session_scope() as session:
        print(views.render_kinds(kind_service.save_kind(session, alias, name)))


@app.command("list")
def list_kinds() -> None:
    with db_connection.session_scope() as session:
        print(views.render_kinds(kind_service.list_kinds(session)))
