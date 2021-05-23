import datetime

from ..config_app import config
from ..helpers.time import scale_time


class Task:
    """
    Hold all data for one task
    """

    default_project = config.default_project
    default_kind = config.default_kind

    def __init__(self):
        self.time: datetime.datetime = None
        self.time_begin: datetime.datetime = None
        self.name: str = ""
        self.project: str = self.default_project
        self.kind: str = self.default_kind

    def get_transformed_time(self):
        """
        Return transformed and scaled time of task with rounding from setting
        """
        time_str = str(self.time)
        time_arr = time_str.split(":")
        time_arr = scale_time(int(time_arr[0]), int(time_arr[1]))
        return float(str(time_arr[0]) + "." + str(time_arr[1]))
