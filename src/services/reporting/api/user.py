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
        self._user = user

    def get_corp_struct_id(self) -> int:
        """
        User corpStructItemId
        """
        return self._user['corpStructItemId']

    def get_id(self) -> int:
        """
        User employeeId
        """
        return self._user['employeeId']

    def update_data(self, data: dict) -> None:
        """
        Update dict of user

        Rewrite exist fields, add new.
        """
        self._user = {**self._user, **data}
