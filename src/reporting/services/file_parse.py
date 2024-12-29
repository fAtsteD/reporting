import datetime
import re
from dataclasses import dataclass
from os import path

import dateutil.parser

from reporting import config, database
from reporting.models import Kind, Project, Report, Task


@dataclass
class TaskLine:
    """
    Simple dto for structure parsed line of task
    """

    time_begin: datetime.datetime = datetime.datetime.now()
    summary: str = ""
    kind: str = ""
    project: str = ""


def parse_task(task_str: str) -> TaskLine:
    """
    Parse line from file to task object
    """
    task = TaskLine()
    split_str = task_str.split(" - ")

    if len(split_str) >= 1 and split_str[0]:
        # Parse time, date will be current, it is not right
        task.time_begin = dateutil.parser.parse(split_str[0].strip().replace(" ", ":"))

    if len(split_str) >= 2 and split_str[1]:
        task.summary = config.dictionary.translate_task(split_str[1].strip().replace("\\-", "-")).replace(
            "\\\\", "\\"
        )

    if len(split_str) >= 3 and split_str[2]:
        task.kind = config.dictionary.translate_kind(split_str[2].strip().replace("\\-", "-").replace("\\\\", "\\"))
    else:
        task.kind = config.app.default_kind

    if len(split_str) >= 4 and split_str[3]:
        task.project = config.dictionary.translate_project(
            split_str[3].strip().replace("\\-", "-").replace("\\\\", "\\")
        )
    else:
        task.project = config.app.default_project

    return task


def parse_reports(read_days: int = 1) -> list[Report]:
    """
    Parse data from the file for some days into Reports and save them to the db.

    It updates existing reports. One day - one report.

    Day in the file divide by 2 new lines.
    Day begins with date and then list of tasks. For example:
    ```
    01.01.2000
    09 00 - task name - kind - project name
    09 43 - task name 2 - kind - project name
    ```

    Equal task name => one task with some periods that summarizes.
    Config has some default information, so it uses if something missed.

    Return reports
    """
    reports: list[Report] = []

    if not path.isfile(config.app.input_file_hours):
        return reports

    database.session.autoflush = False

    with open(config.app.input_file_hours, "r", encoding="utf-8") as input_file_hours:
        # Need for double new line finding
        report: Report | None = None
        day_index = 0
        previous_line = ""
        previous_task_line: TaskLine | None = None
        previous_task: Task | None = None

        for line in input_file_hours:
            if re.search("^[0-9]{1,2}\\.[0-9]{1,2}\\.([0-9]{4}|[0-9]{2})\n$", line):
                report_date = dateutil.parser.parse(line, dayfirst=True).date()
                report = database.session.query(Report).filter(Report.date == report_date).first()

                if report is None:
                    report = Report(date=report_date)
                    database.session.add(report)

                report.remove_tasks()
                reports.append(report)

                continue

            if previous_line == "\n" and line == "\n":
                day_index += 1
                database.session.commit()

                if (
                    report
                    and previous_task
                    and previous_task_line
                    and previous_task_line.summary
                    and report.total_rounded_seconds < config.app.work_day_hours.total_seconds()
                ):
                    previous_task.logged_timedelta(
                        datetime.timedelta(seconds=config.app.work_day_hours.total_seconds() - report.total_seconds)
                    )

                if day_index < read_days or read_days == 0:
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

            task_line = parse_task(line)
            task = None

            if previous_task_line is not None and previous_task is not None:
                previous_task.logged_timedelta(task_line.time_begin - previous_task_line.time_begin)

            if task_line.summary.strip() and task_line.summary not in config.app.skip_tasks:
                for report_task in report.tasks:
                    if (
                        report_task.summary == task_line.summary
                        and report_task.kind.alias == task_line.kind
                        and report_task.project.alias == task_line.project
                    ):
                        task = report_task
                        break

                if task is None:
                    task = Task(summary=task_line.summary)
                    task.report = report

                    if task_line.kind:
                        kind = database.session.query(Kind).filter(Kind.alias == task_line.kind).first()

                        if kind is None:
                            exit(f"Kind {task_line.kind} does not exist")

                        task.kind = kind

                    if task_line.project:
                        project = database.session.query(Project).filter(Project.alias == task_line.project).first()

                        if project is None:
                            exit(f"Project {task_line.project} does not exist")

                        task.project = project

                    database.session.add(task)

            previous_task = task
            previous_task_line = task_line

    database.session.commit()
    return reports
