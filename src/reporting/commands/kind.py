import sqlalchemy as sa
import typer
from sqlalchemy.orm import Session

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

    with db_connection.session_scope() as session:
        kind: Kind | None = session.scalars(sa.select(Kind).where(Kind.alias == alias)).first()

        if kind is None:
            kind = Kind(alias=alias, name=name)
            session.add(kind)
            session.flush()
        else:
            kind.name = name

        _list_kinds(session)


@app.command("list")
def list_kinds() -> None:
    """Print all kinds."""
    config.load_config()

    with db_connection.session_scope() as session:
        _list_kinds(session)


def _list_kinds(session: Session) -> None:
    kinds = session.scalars(sa.select(Kind).order_by(Kind.name)).all()
    print("Kinds:")

    for kind in kinds:
        print(kind)
