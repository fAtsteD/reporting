from reporting.models.kind import Kind


def test_kind_str() -> None:
    alias = "tk"
    name = "Test Kind"
    kind = Kind(alias=alias, name=name)
    assert str(kind) == f"{alias} - {name}"
