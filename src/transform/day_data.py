import datetime

from .task import Task


class DayData():
    """
    Hold all data for current day
    """

    def __init__(self):
        self.date = datetime.date.today()

        self.tasks: list = []
        self.projects: list = []
        self.kinds: list = []

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

    def get_tasks_by_kind(self, kind: str) -> list:
        """
        Return tasks in the defined kind
        """
        result = []

        for task in self.tasks:
            if task.kind == kind:
                result.append(task)

        return result
