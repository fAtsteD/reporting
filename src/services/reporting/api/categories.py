"""
Categories from server
"""


class Categories:
    """
    Save categories from server

    Category dict
    {
        "alias": str,
        "deleted": bool
        "description": str,
        "descriptionEn": str,
        "exportToInvoice": bool,
        "id": int,
        "name": str,
        "nameEn": str,
        "placeholder: str,
        "placeholderEn: str,
        "requireClient": bool,
        "requireInvoiceHours": bool,
        "requireProject": bool,
        "salaryCoefficient": int,
    }

    Category Binding dict
    {
        categoryId: int,
        corpStructItemId: int,
        hideForHead: bool,
        id: int,
        locationPositionId: int,
        orderNumber: int,
        positionId: int,
        roleId: int,
    }
    """

    def __init__(self, categories: list, categories_binding: list) -> None:
        """
        Initialize object with data from request of server
        """
        self._categories = categories
        self._categories_binding = categories_binding

    def get_by_name(self, name: str, corp_struct_id: str) -> dict:
        """
        Retrieve id from categories
        """
        if len(self._categories) == 0 or len(self._categories_binding) == 0:
            return {}

        allowed_categories = set(map(
            lambda category_binding: category_binding["categoryId"],
            filter(
                lambda category_binding: category_binding["corpStructItemId"] == corp_struct_id,
                self._categories_binding
            )
        ))

        user_categories = list(filter(
            lambda category: category["id"] in allowed_categories,
            self._categories
        ))

        for category in user_categories:
            if category["name"] == name:
                return category

        return {}
