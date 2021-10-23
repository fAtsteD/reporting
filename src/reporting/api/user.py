"""
User data from server
"""


class User:
    """
    User data in dict

    User dict:
    {
        Init query:
        "id": int,
        "login": str,
        "email": str,
        "locale": str,
        "fullName": str,
        "position": str,
        "sex": int,

        Position query:
        "locationId": int,
        "positionId": int,
        "corpStructItemId": int,
        "acting": bool
    }
    """

    def __init__(self, user: dict) -> None:
        self.user = user

    def update_data(self, data: dict) -> None:
        """
        Update dict of user

        Rewrite exist fields, add new.
        """
        self.user = {**self.user, **data}
