from reporting.qatestlab_portal.models import (
    Category,
    CategoryBinding,
    CategoryCollection,
    CorpStructItem,
    CorpStructItemCollection,
)
from tests.factories.portal_api import (
    PortalCategoryBindingFactory,
    PortalCategoryFactory,
    PortalCorpStructItemFactory,
)

_CORP_STRUCT_ITEM_ID = 7


def test_finds_no_category_when_no_name_matches() -> None:
    category, binding = _bound_category("Develop")
    collection = CategoryCollection(categories=[category], categories_binding=[binding])

    assert collection.get_by_name_and_corp_struct_item("Analysis", _CORP_STRUCT_ITEM_ID) is None


def test_finds_no_category_when_the_name_is_bound_to_another_corp_struct_item() -> None:
    category, binding = _bound_category("Develop")
    collection = CategoryCollection(categories=[category], categories_binding=[binding])

    assert collection.get_by_name_and_corp_struct_item("Develop", _CORP_STRUCT_ITEM_ID + 1) is None


def test_finds_no_corp_struct_item_for_an_unknown_alias() -> None:
    collection = CorpStructItemCollection(corp_struct_items=[PortalCorpStructItemFactory.build(alias="OTHER")])

    assert collection.get_by_alias("WANTED") is None


def test_finds_no_corp_struct_item_for_an_unknown_id() -> None:
    item: CorpStructItem = PortalCorpStructItemFactory.build()
    collection = CorpStructItemCollection(corp_struct_items=[item])

    assert collection.get_by_id(item.id + 1000) is None


def test_finds_the_category_bound_to_the_corp_struct_item_by_name() -> None:
    other_category, other_binding = _bound_category("Analysis")
    wanted_category, wanted_binding = _bound_category("Develop")
    collection = CategoryCollection(
        categories=[other_category, wanted_category],
        categories_binding=[other_binding, wanted_binding],
    )

    assert collection.get_by_name_and_corp_struct_item("Develop", _CORP_STRUCT_ITEM_ID) is wanted_category


def test_finds_the_corp_struct_item_by_alias() -> None:
    other_item = PortalCorpStructItemFactory.build(alias="OTHER")
    wanted_item = PortalCorpStructItemFactory.build(alias="WANTED")
    collection = CorpStructItemCollection(corp_struct_items=[other_item, wanted_item])

    assert collection.get_by_alias("WANTED") is wanted_item


def test_finds_the_corp_struct_item_by_id() -> None:
    other_item = PortalCorpStructItemFactory.build()
    wanted_item = PortalCorpStructItemFactory.build()
    collection = CorpStructItemCollection(corp_struct_items=[other_item, wanted_item])

    assert collection.get_by_id(wanted_item.id) is wanted_item


def _bound_category(name: str) -> tuple[Category, CategoryBinding]:
    category = PortalCategoryFactory.build(name=name)
    binding = PortalCategoryBindingFactory.build(
        category_id=category.id,
        corp_struct_item_id=_CORP_STRUCT_ITEM_ID,
    )

    return category, binding
