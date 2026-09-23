from factory.base import Factory
from factory.declarations import Sequence
from factory.faker import Faker

from reporting.qatestlab_portal.models import (
    Category,
    CategoryBinding,
    Client,
    CorpStructItem,
    Employee,
    EmployeePosition,
    PortalBaseModel,
    Project,
    Report,
)


class BaseFactory[FactoryModelType: PortalBaseModel](Factory[FactoryModelType]):
    class Meta:  # pyright: ignore
        abstract = True


class PortalCategoryBindingFactory(BaseFactory[CategoryBinding]):
    class Meta:  # pyright: ignore
        model = CategoryBinding

    category_id = Sequence(lambda index: index + 1)
    corp_struct_item_id = Sequence(lambda index: index + 1)
    id = Sequence(lambda index: index + 1)
    position_id = Sequence(lambda index: index + 1)
    role_id = Sequence(lambda index: index + 1)


class PortalCategoryFactory(BaseFactory[Category]):
    class Meta:  # pyright: ignore
        model = Category

    alias = Sequence(lambda index: f"CATEGORY{index}")
    deleted = False
    id = Sequence(lambda index: index + 1)
    name = Faker("sentence", nb_words=3, variable_nb_words=True)
    salary_coefficient = Faker("random_int", min=1, max=10)


class PortalClientFactory(BaseFactory[Client]):
    class Meta:  # pyright: ignore
        model = Client

    id = Sequence(lambda index: index + 1)
    name = Faker("company")


class PortalCorpStructItemFactory(BaseFactory[CorpStructItem]):
    class Meta:  # pyright: ignore
        model = CorpStructItem

    alias = Sequence(lambda index: f"CORP{index}")
    id = Sequence(lambda index: index + 1)
    name = Faker("sentence", nb_words=3, variable_nb_words=True)


class PortalEmployeeFactory(BaseFactory[Employee]):
    class Meta:  # pyright: ignore
        model = Employee

    email = Faker("email")
    first_name = Faker("first_name")
    id = Sequence(lambda index: index + 1)
    last_name = Faker("last_name")


class PortalEmployeePositionFactory(BaseFactory[EmployeePosition]):
    class Meta:  # pyright: ignore
        model = EmployeePosition

    acting = False
    alias = Sequence(lambda index: f"POSITION{index}")
    corp_struct_item_alias = Sequence(lambda index: f"CORP{index}")
    corp_struct_item_id = Sequence(lambda index: index + 1)
    employee_id = Sequence(lambda index: index + 1)
    id = Sequence(lambda index: index + 1)
    position_id = Sequence(lambda index: index + 1)


class PortalProjectFactory(BaseFactory[Project]):
    class Meta:  # pyright: ignore
        model = Project

    active = True
    id = Sequence(lambda index: index + 1)
    name = Faker("sentence", nb_words=3, variable_nb_words=True)


class PortalReportFactory(BaseFactory[Report]):
    class Meta:  # pyright: ignore
        model = Report

    date = Faker("date_object")
    employee_id = Sequence(lambda index: index + 1)
    have_problems = False
    id = Sequence(lambda index: index + 1)
    no_tasks = False
    problems = ""
