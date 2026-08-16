import typer

from reporting import config
from reporting.database import db_connection
from reporting.database.models import Kind

app = typer.Typer(help="Manage kinds")


@app.command("add")
def add(
    alias: str = typer.Argument(..., help="Kind alias (unique)"),
    name: str = typer.Argument(..., help="Kind name"),
) -> None:
    """Add or update kind."""
    config.load_config()
    kind: Kind | None = db_connection.session.query(Kind).filter(Kind.alias == alias).first()

    if kind is None:
        kind = Kind(alias=alias, name=name)
        db_connection.session.add(kind)
    else:
        kind.name = name

    db_connection.session.commit()
    list_kinds()


@app.command("list")
def list_kinds() -> None:
    """Print all kinds."""
    kinds = db_connection.session.query(Kind).order_by(Kind.name).all()
    print("Kinds:")

    for kind in kinds:
        print(kind)
