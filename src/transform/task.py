import datetime

from ..config_app import config
from ..helpers.time import scale_time


class Task:
    """
    Hold all data for one task
    """

    def __init__(self):
        self.time: datetime.timedelta = None
        self.time_begin: datetime.datetime = None
        self.name: str = ""
        self.project: str = config.default_project
        self.kind: str = config.default_kind

    def get_transformed_time(self) -> float:
        """
        Rounded time from 60 minutes to 100 and return like float value of hours
        """
        time_str = str(self.time)
        time_arr = time_str.split(":")
        time_arr = scale_time(int(time_arr[0]), int(time_arr[1]))
        return float(str(time_arr[0]) + "." + str(time_arr[1]))
