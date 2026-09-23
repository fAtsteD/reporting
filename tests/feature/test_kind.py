import sqlalchemy as sa
from sqlalchemy.orm import Session

from reporting.database.models import Kind
from tests.assertions import cli_output
from tests.factories.database import KindFactory
from tests.fixtures.cli import RunCli


def test_kind_add_saves_the_kind_and_prints_the_kinds(
    database_session: Session,
    run_cli: RunCli,
) -> None:
    result = run_cli("kind", "add", "dev", "Develop")

    cli_output.assert_lines(result.out, ["Kinds", "dev Develop"])
    saved_kind = database_session.scalars(sa.select(Kind)).one()
    assert (saved_kind.alias, saved_kind.name) == ("dev", "Develop")


def test_kind_add_without_arguments_is_a_usage_error(run_cli: RunCli) -> None:
    failure = run_cli("kind", "add")

    assert failure.exit_code == 2
    assert failure.out == ""
    assert failure.err != ""


def test_kind_list_prints_the_stored_kinds(
    run_cli: RunCli,
) -> None:
    KindFactory.create(alias="k1", name="Alpha")
    KindFactory.create(alias="k2", name="Beta")

    result = run_cli("kind", "list")

    cli_output.assert_lines(result.out, ["Kinds", "k1 Alpha", "k2 Beta"])
