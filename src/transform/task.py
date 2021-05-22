import datetime


class Task:
    """
    Hold all data for one task
    """

    def __init__(self):
        self.time: datetime.datetime = None
        self.name: str = ""
        self.project: str = ""
        self.kind: str = ""
