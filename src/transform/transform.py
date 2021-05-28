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
from .task import Task

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
    _summarize_tasks(day_data, one_day_tasks)

    return day_data


def _read_one_day(data: DayData) -> list:
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

            task = _parse_task(line)
            one_day.append(_parse_task(line))

            if not task.kind in data.kinds:
                data.kinds.append(task.kind)

            if not task.project in data.projects:
                data.projects.append(task.project)

    return one_day


def _parse_task(task_str: str) -> Task:
    """
    Parse string to dict of date, name of task, kind, project

    Returning dictionary
    """
    result = Task()

    split_str = task_str.split(" - ")

    if (len(split_str) >= 1):
        # Parse time, date will be current, it is not right
        result.time_begin = dateutil.parser.parse(
            split_str[0].replace(" ", ":").strip())

    if (len(split_str) >= 2):
        # Parse task
        result.name = config.dictionary.translate_task(
            split_str[1].strip().replace('\-', '-'))

    if (len(split_str) >= 3):
        # Parse project
        result.kind = config.dictionary.translate_kind(
            split_str[2].strip().replace('\-', '-'))

    if (len(split_str) >= 4):
        # Parse project
        result.project = config.dictionary.translate_project(
            split_str[3].strip().replace('\-', '-'))

    return result


def _summarize_tasks(data: DayData, one_day: list):
    """
    Summarize tasks, set their duration
    """
    sum_time = dateutil.parser.parse("00:00")
    num_one_day_tasks = len(one_day)

    for i in range(num_one_day_tasks):
        if (one_day[i].name == "") or (one_day[i].name in config.skip_tasks):
            continue

        task = one_day[i]
        delta_time = None

        if i == num_one_day_tasks - 1:
            delta_time = config.work_day_hours - sum_time
        else:
            delta_time = one_day[i + 1].time_begin - task.time_begin

        sum_time += delta_time

        exist_task = data.get_task_by_name(task.name)
        if exist_task is None:
            task.time = delta_time
            data.tasks.append(task)
            continue

        exist_task.time += delta_time
