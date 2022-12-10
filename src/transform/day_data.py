import datetime

from .task import Task
from ..config_app import config


class DayData():
    """
    Hold all data for current day
    """

    def __init__(self):
        self.date = datetime.date.today()

        self.tasks: list[Task] = []
        self.projects: list[str] = []
        self.kinds: list[str] = []

    def is_exist(self, task_name: str) -> bool:
        """
        Check if task is setted. Name of task is unique
        """
        if len(self.tasks) < 1:
            return False

        for task in self.tasks:
            if task.name == task_name:
                return True

        return False

    def get_task_by_name(self, task_name: str) -> Task:
        """
        Rerurn existing task by name
        """
        if not self.is_exist(task_name):
            return None

        for i in range(len(self.tasks)):
            if self.tasks[i].name == task_name:
                return self.tasks[i]

    def get_tasks_by_kind(self, kind: str) -> list[Task]:
        """
        Return tasks in the defined kind
        """
        result = []

        for task in self.tasks:
            if task.kind == kind:
                result.append(task)

        return result

    def get_leaved_time(self) -> datetime.timedelta:
        """
        Return time leaves before end of the day

        It uses scaled time for computation.
        """
        sum_time = datetime.timedelta(hours=0, minutes=0)
        for task in self.tasks:
            sum_time += task.get_scaled_time()

        return config.work_day_hours - sum_time
