"""
Object for holding positions
"""


class Positions:
    """
    Hold positions and related function

    Project:
    {
        "id": int,
        "employeeId": int,
        "locationId": int,
        "positionId": int,
        "corpStructItemId": int,
        "acting": bool
    }
    """

    def __init__(self, positions: list) -> None:
        """
        Init position object
        """
        self.positions = positions

    def get_by_user_id(self, user_id: str) -> dict:
        """
        Return position dictionary by user id
        """
        if len(self.positions) == 0:
            return None

        for position in self.positions:
            if position["employeeId"] == user_id:
                return position

        return None
