class Projects:
    """
    Hold projects and related function
    It has projects from request

    Project:
    {
        "id": int,
        "externalId": str,
        "name": str,
        "status": str,
        "active": bool,
        "provider": int,
        "clientId": int
    }
    """

    def __init__(self, projects: list) -> None:
        """
        Init project object
        """
        self.projects = projects

    def get_by_name(self, name: str) -> dict:
        """
        Return project dictionary by name
        """
        if len(self.projects) == 0:
            return None
