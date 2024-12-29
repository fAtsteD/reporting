import faker
import pytest
from sqlalchemy.orm import Session

from reporting import cli
from reporting.models import Kind
from tests.conftest import ReportingConfigFixture
from tests.factories import KindFactory


def test_add_kind(
    capsys: pytest.CaptureFixture,
    database_session: Session,
    reporting_config: ReportingConfigFixture,
) -> None:
    reporting_config()
    kind_raw = {
        "alias": "legal-witch",
        "name": "Principal Group Associate",
    }
    output_expected = "Kinds:\n"
    output_expected += f"{kind_raw['alias']} - {kind_raw['name']}\n"

    cli.main(["--kind", kind_raw["alias"], kind_raw["name"]])

    output = capsys.readouterr()
    assert output.out == (output_expected)

    saved_kind = database_session.query(Kind).first()
    assert saved_kind is not None
    assert saved_kind.alias == kind_raw["alias"]
    assert saved_kind.name == kind_raw["name"]


def test_show_kinds(
    capsys: pytest.CaptureFixture,
    reporting_config: ReportingConfigFixture,
) -> None:
    reporting_config()
    kinds: list[Kind] = [
        KindFactory.create(tasks=[]),
        KindFactory.create(tasks=[]),
        KindFactory.create(tasks=[]),
    ]
    kinds.sort(key=lambda kind: kind.name)
    output_expected = "Kinds:\n"

    for kind in kinds:
        output_expected += f"{kind}\n"

    cli.main(["--show-kinds"])

    output = capsys.readouterr()
    assert output.out == (output_expected)


def test_show_kinds_empty(
    capsys: pytest.CaptureFixture,
    reporting_config: ReportingConfigFixture,
) -> None:
    reporting_config()
    output_expected = "Kinds:\n"

    cli.main(["--show-kinds"])

    output = capsys.readouterr()
    assert output.out == (output_expected)


def test_update_kind(
    capsys: pytest.CaptureFixture,
    database_session: Session,
    faker: faker.Faker,
    reporting_config: ReportingConfigFixture,
) -> None:
    reporting_config()
    kind: Kind = KindFactory.create(tasks=[])
    kind_name_new = faker.sentence(nb_words=3, variable_nb_words=True)
    output_expected = "Kinds:\n"
    output_expected += f"{kind.alias} - {kind_name_new}\n"

    cli.main(["--kind", kind.alias, kind_name_new])

    output = capsys.readouterr()
    assert output.out == (output_expected)

    saved_kind = database_session.query(Kind).first()
    assert saved_kind is not None
    assert saved_kind.alias == kind.alias
    assert saved_kind.name == kind_name_new
