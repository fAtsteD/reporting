from reporting.models.project import Project


def test_kind_str() -> None:
    alias = "tp"
    name = "Test Project"
    kind = Project(alias=alias, name=name)
    assert str(kind) == f"{alias} - {name}"
