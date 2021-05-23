"""
User data from server
"""


class User:
    """
    User data in dict

    User dict:
    {
        "id": int,
        "login": str,
        "email": str,
        "locale": str,
        "fullName": str,
        "position": str,
        "sex": int,
        "departmentId": int
    }
    """

    def __init__(self, user: dict) -> None:
        self.user = user
