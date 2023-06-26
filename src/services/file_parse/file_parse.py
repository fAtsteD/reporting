import datetime
import re
from os import path

import dateutil.parser

from config_app import config
from models.report import Report
from models.task import Task

from .task_line import TaskLine


class FileParse:
    """
    Parse data from the file for one day

    Day in the file divide by 2 new lines.
    Day begins with date and then list of tasks. For example:
    ```
    01.01.2000
    09 00 - task name - kind - project name
    09 43 - task name 2 - kind - project name
    ```

    Equal task name => one task with some periods that summarizes.
    Config has default project, so it uses if project name
    does not set.
    """

    # Path to the file
    filepath: str = ''
    # How many days parse, 0 - read all days
    read_days: int = 1

    def __init__(self, filepath: str, read_days: int = 1):
        self.filepath = filepath
        self.read_days = read_days

    def reports(self) -> list[Report]:
        """
        Parse days and return thier reports

        It parse and save/update reports to the db before return them.
        One day - one report, so it updates existed reports.
        """
        reports: list[Report] = []

        if not path.isfile(config.input_file_hours):
            return reports

        with open(config.input_file_hours, "r", encoding="utf-8") as input_file_hours:
            # Need for double new line finding
            report = None
            day_index = 0
            previous_line = ""
            previous_task_line: TaskLine = None
            previous_task: Task = None

            for line in input_file_hours:
                if (re.search("^[0-9]{1,2}\.[0-9]{1,2}\.([0-9]{4}|[0-9]{2})\n$", line)):
                    report_date = dateutil.parser.parse(
                        line, dayfirst=True).date()
                    report = config.sqlite_session.query(
                        Report).filter(Report.date == report_date).first()

                    if report is None:
                        report = Report(date=report_date)
                        config.sqlite_session.add(report)

                    report.remove_tasks()
                    config.sqlite_session.commit()
                    reports.append(report)

                    continue

                if previous_line == "\n" and line == "\n":
                    day_index += 1

                    if previous_task_line.summary and report.total_seconds() < config.work_day_hours.total_seconds():
                        previous_task.logged_timedelta(datetime.timedelta(
                            seconds=config.work_day_hours.total_seconds() - report.total_seconds()))

                    if day_index < self.read_days:
                        report = None
                        previous_line = ""
                        previous_task_line = None
                        previous_task = None
                        continue

                    break
                else:
                    previous_line = line

                if not line.strip() or report is None:
                    continue

                task_line = self._parse_task(line)
                task = None

                if previous_task_line is not None and previous_task is not None:
                    previous_task.logged_timedelta(
                        task_line.time_begin - previous_task_line.time_begin)

                if task_line.summary.strip() and task_line.summary not in config.skip_tasks:
                    task = config.sqlite_session.query(Task)\
                        .filter(Task.report.has(Report.date == report_date))\
                        .filter(Task.summary == task_line.summary)\
                        .filter(Task.kind == task_line.kind)\
                        .filter(Task.project == task_line.project)\
                        .first()

                    if task is None:
                        task = Task(summary=task_line.summary)

                        if task_line.kind:
                            task.kind = task_line.kind

                        if task_line.project:
                            task.project = task_line.project

                        report.tasks.append(task)
                        config.sqlite_session.add(task)

                previous_task = task
                previous_task_line = task_line

        config.sqlite_session.commit()
        return reports

    def _parse_task(self, task_str: str) -> TaskLine:
        """
        Parse line from file to task object
        """
        task = TaskLine()
        split_str = task_str.split(" - ")

        if (len(split_str) >= 1):
            # Parse time, date will be current, it is not right
            task.time_begin = dateutil.parser.parse(
                split_str[0].replace(" ", ":").strip())

        if (len(split_str) >= 2):
            # Parse task
            task.summary = config.dictionary.translate_task(
                split_str[1].strip().replace('\-', '-')).replace('\\\\', '\\')

        if (len(split_str) >= 3):
            # Parse project
            task.kind = config.dictionary.translate_kind(
                split_str[2].strip().replace('\-', '-')).replace('\\\\', '\\')
        else:
            task.kind = config.default_kind

        if (len(split_str) >= 4):
            # Parse project
            task.project = config.dictionary.translate_project(
                split_str[3].strip().replace('\-', '-')).replace('\\\\', '\\')
        else:
            task.project = config.default_project

        return task
