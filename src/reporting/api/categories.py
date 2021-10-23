"""
Categories from server
"""


class Categories:
    """
    Save categories from server

    Category dict
    {
        "id": int,
        "name": str,
        "nameEn": str,
        "alias": str,
        "requireClient": bool,
        "requireProject": bool,
        "requireInvoiceHours": bool,
        "salaryCoefficient": int,
        "categoryDepartmentDtos": [
            {
                "departmentId": int,
                "orderNumber": int
            },
        ],
        "description": str,
        "descriptionEn": str,
        "exportToInvoice": bool,
        "deleted": bool
    }
    """

    def __init__(self, categories: list) -> None:
        """
        Initialize object with data from request of server
        """
        self.categories = categories

    def get_by_name(self, name: str, corp_struct_id: str) -> dict:
        """
        Retrieve id from categories
        """
        if len(self.categories) == 0:
            return None

        def check_corp_struct_id(departments: list) -> bool:
            for department in departments:
                if department["corpStructItemId"] == corp_struct_id:
                    return True

            return False

        for category in self.categories:
            if category["name"] == name and check_corp_struct_id(category["categoryDepartmentDtos"]):
                return category

        return None
