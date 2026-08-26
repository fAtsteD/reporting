import sqlalchemy as sa
from sqlalchemy.orm import Session

from reporting.database.models import Kind
from tests import rendered_output
from tests.conftest import ReportingConfigFixture
from tests.factories import KindFactory
from tests.fixtures.cli import RunCli


def test_add_kind(
    database_session: Session,
    reporting_config: ReportingConfigFixture,
    run_cli: RunCli,
) -> None:
    reporting_config()

    result = run_cli("kind", "add", "legal-witch", "Principal Group Associate")

    assert rendered_output.cells(result.out) == [
        ["Kinds"],
        ["legal-witch", "Principal Group Associate"],
    ]

    saved_kind = database_session.scalars(sa.select(Kind)).first()
    assert saved_kind is not None
    assert saved_kind.alias == "legal-witch"
    assert saved_kind.name == "Principal Group Associate"


def test_show_kinds(
    reporting_config: ReportingConfigFixture,
    run_cli: RunCli,
) -> None:
    reporting_config()
    KindFactory.create(alias="k3", name="Gamma", tasks=[])
    KindFactory.create(alias="k1", name="Alpha", tasks=[])
    KindFactory.create(alias="k2", name="Beta", tasks=[])

    result = run_cli("kind", "list")

    assert rendered_output.cells(result.out) == [
        ["Kinds"],
        ["k1", "Alpha"],
        ["k2", "Beta"],
        ["k3", "Gamma"],
    ]


def test_show_kinds_empty(
    reporting_config: ReportingConfigFixture,
    run_cli: RunCli,
) -> None:
    reporting_config()

    result = run_cli("kind", "list")

    assert rendered_output.cells(result.out) == [["Kinds"], ["No kinds yet"]]


def test_update_kind(
    database_session: Session,
    reporting_config: ReportingConfigFixture,
    run_cli: RunCli,
) -> None:
    reporting_config()
    KindFactory.create(alias="k1", name="Old Name", tasks=[])

    result = run_cli("kind", "add", "k1", "New Name")
    database_session.expire_all()

    assert rendered_output.cells(result.out) == [["Kinds"], ["k1", "New Name"]]

    saved_kind = database_session.scalars(sa.select(Kind)).first()
    assert saved_kind is not None
    assert saved_kind.alias == "k1"
    assert saved_kind.name == "New Name"


def test_add_kind_without_arguments_is_a_usage_error(run_cli: RunCli) -> None:
    failure = run_cli("kind", "add")

    assert failure.exit_code == 2
    assert failure.out == ""
    assert failure.err != ""


def test_show_kinds_renders_a_panel(
    reporting_config: ReportingConfigFixture,
    run_cli: RunCli,
) -> None:
    reporting_config()
    KindFactory.create(alias="k1", name="Alpha", tasks=[])
    KindFactory.create(alias="k2", name="Beta", tasks=[])

    result = run_cli("kind", "list")

    assert result.out == (
        "\u256d\u2500 Kinds \u2500\u2500\u2500\u256e\n"
        "\u2502 k1  Alpha \u2502\n"
        "\u2502 k2  Beta  \u2502\n"
        "\u2570\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u256f\n"
    )
