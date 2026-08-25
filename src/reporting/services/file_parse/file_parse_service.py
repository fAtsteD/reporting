import datetime
import re
from os import path

import dateutil.parser
import sqlalchemy as sa
from sqlalchemy.orm import Session

from reporting import config
from reporting.database.models import Kind, Project, Report, Task
from reporting.services.file_parse.exceptions import (
    FileParseError,
    FileParseNotConfiguredError,
    UnknownKindError,
    UnknownProjectError,
)
from reporting.services.file_parse.models import TaskLine


def parse_task(task_str: str, report_date: datetime.date) -> TaskLine:
    parsed_time = _parse_time(task_str.split(" - ")[0].strip().replace(" ", ":"), task_str)
    task = TaskLine(
        time_begin=datetime.datetime.combine(report_date, parsed_time, tzinfo=config.app.timezone),
    )
    split_str = task_str.split(" - ")

    if len(split_str) >= 2 and split_str[1]:
        task.summary = config.dictionary.translate_task(split_str[1].strip().replace("\\-", "-")).replace("\\\\", "\\")

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


def clear_report_tasks(session: Session, report: Report) -> None:
    for task in report.tasks:
        session.delete(task)

    report.updated_at = datetime.datetime.now(datetime.UTC)
    session.commit()


def parse_reports(session: Session, read_days: int = 1) -> list[Report]:
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
    if not config.app.input_file_hours:
        raise FileParseNotConfiguredError("Path to the file with tasks by hours is not configured")

    input_file_path = path.normpath(path.expanduser(config.app.input_file_hours))

    if not path.isfile(input_file_path):
        raise FileParseNotConfiguredError(f"File with tasks by hours does not exist: {input_file_path}")

    reports: list[Report] = []
    skip_tasks = [config.dictionary.translate_task(task_name) for task_name in config.app.skip_tasks]

    with open(input_file_path, "r", encoding="utf-8") as input_file_hours:
        report: Report | None = None
        day_index = 0
        previous_line = ""
        previous_task_line: TaskLine | None = None
        previous_task: Task | None = None

        for line in input_file_hours:
            if re.search("^[0-9]{1,2}\\.[0-9]{1,2}\\.([0-9]{4}|[0-9]{2})\n$", line):
                report_date = _parse_date(line)
                report = session.scalars(sa.select(Report).where(Report.date == report_date)).first()

                if report is None:
                    report = Report(date=report_date)
                    session.add(report)
                    session.flush()

                clear_report_tasks(session, report)
                reports.append(report)

                continue

            if previous_line == "\n" and line == "\n":
                day_index += 1
                session.commit()

                if (
                    report
                    and previous_task
                    and previous_task_line
                    and previous_task_line.summary
                    and report.total_rounded_seconds < config.app.work_day_duration.total_seconds()
                ):
                    previous_task.logged_timedelta(
                        datetime.timedelta(seconds=config.app.work_day_duration.total_seconds() - report.total_seconds)
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

            task_line = parse_task(line, report.date)
            task = None

            if previous_task_line is not None and previous_task is not None:
                previous_task.logged_timedelta(task_line.time_begin - previous_task_line.time_begin)

            if task_line.summary.strip() and task_line.summary not in skip_tasks:
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
                        task.kind = _resolve_kind(session, task_line.kind)

                    if task_line.project:
                        task.project = _resolve_project(session, task_line.project)

                    session.add(task)
                    session.flush()

            previous_task = task
            previous_task_line = task_line

    session.commit()

    return reports


def _parse_date(line: str) -> datetime.date:
    try:
        return dateutil.parser.parse(line, dayfirst=True).date()
    except (dateutil.parser.ParserError, OverflowError) as error:
        raise FileParseError(f"Line is not a date (DD.MM.YYYY): {line.strip()}") from error


def _parse_time(time_str: str, task_str: str) -> datetime.time:
    try:
        return dateutil.parser.parse(time_str).time()
    except (dateutil.parser.ParserError, OverflowError) as error:
        raise FileParseError(f"Line does not start with a time (HH MM): {task_str.strip()}") from error


def _resolve_kind(session: Session, alias: str) -> Kind:
    kind = session.scalars(sa.select(Kind).where(Kind.alias == alias)).first()

    if kind is None:
        raise UnknownKindError(f'Kind {alias} does not exist. Add it: reporting kind add {alias} "<name>"')

    return kind


def _resolve_project(session: Session, alias: str) -> Project:
    project = session.scalars(sa.select(Project).where(Project.alias == alias)).first()

    if project is None:
        raise UnknownProjectError(f'Project {alias} does not exist. Add it: reporting project add {alias} "<name>"')

    return project
