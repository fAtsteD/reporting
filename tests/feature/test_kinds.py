import sqlalchemy as sa
from sqlalchemy.orm import Session

from reporting.database.models import Kind
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

    assert result.out == "Kinds:\nlegal-witch - Principal Group Associate\n"

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

    assert result.out == "Kinds:\nk1 - Alpha\nk2 - Beta\nk3 - Gamma\n"


def test_show_kinds_empty(
    reporting_config: ReportingConfigFixture,
    run_cli: RunCli,
) -> None:
    reporting_config()

    result = run_cli("kind", "list")

    assert result.out == "Kinds:\n"


def test_update_kind(
    database_session: Session,
    reporting_config: ReportingConfigFixture,
    run_cli: RunCli,
) -> None:
    reporting_config()
    KindFactory.create(alias="k1", name="Old Name", tasks=[])

    result = run_cli("kind", "add", "k1", "New Name")
    database_session.expire_all()

    assert result.out == "Kinds:\nk1 - New Name\n"

    saved_kind = database_session.scalars(sa.select(Kind)).first()
    assert saved_kind is not None
    assert saved_kind.alias == "k1"
    assert saved_kind.name == "New Name"


def test_add_kind_without_arguments_is_a_usage_error(run_cli: RunCli) -> None:
    failure = run_cli("kind", "add")

    assert failure.exit_code == 2
    assert failure.out == ""
    assert failure.err != ""
