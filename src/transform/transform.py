#!/usr/bin/python3

"""
Transform file with hours to daily report

Every line consist:

[time to start task] - [name of task] - [name of project]

All undefined tasks, except that is in the except task list,
will be in the internal tasks

Variables of DayData:
- date - date of report from input file
- one_day_projects - dictionaty with task by projects and sum of time for each task
"""

import re

import dateutil.parser

from ..config_app import config
from ..helpers.time import *
from .day_data import DayData

TIME = "time"
TASK = "task"
PROJECT = "project"

DEFAULT_PROJECT = "Внутренние задачи"


def get_day_data():
    """
    Return object with parsed data for the day
    """
    day_data = DayData()

    one_day_tasks = _read_one_day(day_data)
    _group_by_project(day_data, one_day_tasks)

    return day_data


def _read_one_day(data: DayData) -> DayData:
    """
    Read all tasks for one day to array
    """
    one_day = []

    with open(config.input_file_hours, "r", encoding="utf-8") as input_file_hours:
        # Need for double new line finding
        previous_line = ""
        for line in input_file_hours:
            if (re.search("^[0-9]{1,2}\.[0-9]{1,2}\.([0-9]{4}|[0-9]{2})\n$", line)):
                data.date = dateutil.parser.parse(line, dayfirst=True)
                continue

            if previous_line == "\n" and line == "\n":
                break
            else:
                previous_line = line

            if line == "\n":
                continue

            one_day.append(_parse_task(line))

    return one_day


def _parse_task(task_str: str) -> dict:
    """
    Parse string to array of date, name of task, name of project

    Returning dictionary
    """
    result = {}

    split_str = task_str.split(" - ")

    if (len(split_str) >= 1):
        # Parse time, date will be current, it is not right
        result[TIME] = dateutil.parser.parse(
            split_str[0].replace(" ", ":").strip())

    if (len(split_str) >= 2):
        # Parse task
        result[TASK] = split_str[1].strip()

    if (len(split_str) >= 3):
        # Parse project
        result[PROJECT] = split_str[-1].strip()

    return result


def _group_by_project(data: DayData, one_day: list):
    """
    Group tasks by project
    """
    sum_time = dateutil.parser.parse("00:00")
    num_one_day_tasks = len(one_day)
    for i in range(num_one_day_tasks):
        if (not TASK in one_day[i]) or (one_day[i][TASK] in config.skip_tasks):
            continue

        task = one_day[i][TASK]

        project = ""
        if PROJECT in one_day[i]:
            project = one_day[i][PROJECT]
        else:
            project = DEFAULT_PROJECT

        if not project in data.one_day_projects:
            data.one_day_projects[project] = {}

        if i == num_one_day_tasks - 1:
            delta_time = config.work_day_hours - sum_time
        else:
            delta_time = (one_day[i + 1][TIME] -
                          one_day[i][TIME])

        if task in data.one_day_projects[project].keys():
            data.one_day_projects[project][task] += delta_time
        else:
            data.one_day_projects[project][task] = delta_time

        sum_time += delta_time

    # Transform resulting time
    _transform_time(data)


def _transform_time(data: DayData):
    """
    Transform time [hours]:[minutes]:[seconds] to [hours].[minutes relative]
    """
    for project in data.one_day_projects:
        for task in data.one_day_projects[project]:
            time_str = str(data.one_day_projects[project][task])
            time_arr = time_str.split(":")
            time_arr = _scale_time(int(time_arr[0]), int(time_arr[1]))
            data.one_day_projects[project][task] = str(time_arr[0]) + "." + \
                str(time_arr[1])


def _scale_time(hours: int, minutes: int) -> list:
    """
    Transform minutes 0 to 60 gap to 0 to 100 gap with rounding minutes to 25
    """
    minutes = remap(minutes, 0, 60, 0, 100)

    # Fractional part rounded to 25
    frac = minutes % config.minute_round_to
    if frac >= int(config.minute_round_to / 2) + 1:
        minutes = (minutes // config.minute_round_to + 1) * \
            config.minute_round_to
        if minutes == 100:
            hours += 1
            minutes = 0
    else:
        minutes = minutes // config.minute_round_to * config.minute_round_to

    return [int(hours), int(minutes)]
