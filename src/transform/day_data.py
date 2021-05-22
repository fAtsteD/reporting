import datetime


class DayData():
    """
    Hold all data for current day
    """

    default_project = "Default"
    default_kind = "Development"

    def __init__(self):
        self.date = datetime.date.today()
        self.one_day_projects = {}

        self.tasks: list = []
        self.projects: list = []
        self.kinds: list = []
