#!/usr/bin/python3

"""
File with class for transform hours to daily report
"""

import datetime
import re
import sys

import dateutil.parser


class Transform():
    """
    Transform file with hours to daily report

    Every line consist:

    [time to start task] - [name of task] - [name of project]

    All undefined tasks, except that is in the except task list,
    will be in the internal tasks

    Variables:    - input_file_hours - input file tasks by hours
    - date - date of report from input file
    - one_day - array with dictionary task by hours
    - one_day_projects - dictionaty with task by projects and sum of time for each task
    """

    TIME = "time"
    TASK = "task"
    PROJECT = "project"

    DEFAULT_PROJECT = "Внутренние задачи"

    def __init__(self, config):
        self.config = config
        self.input_file_hours = open(
            config.input_file_hours, "r", encoding="utf-8")

        self.read_one_day()
        self.group_by_project()

    def read_one_day(self):
        """
        Read all tasks for one day to array
        """
        self.one_day = []
        # Need for double new line finding
        previous_line = ""
        for line in self.input_file_hours:
            if (re.search("^[0-9]{1,2}\.[0-9]{1,2}\.([0-9]{4}|[0-9]{2})\n$", line)):
                self.date = dateutil.parser.parse(line)
                continue

            if previous_line == "\n" and line == "\n":
                break
            else:
                previous_line = line

            if line == "\n":
                continue

            self.one_day.append(self.parse_task(line))

    def parse_task(self, task_str: str):
        """
        Parse string to array of date, name of task, name of project

        Returning dictionary
        """
        result = {}

        split_str = task_str.split(" - ")

        if (len(split_str) >= 1):
            # Parse time, date will be cuurent, it is not right
            result[self.TIME] = dateutil.parser.parse(
                split_str[0].replace(" ", ":").strip())

        if (len(split_str) >= 2):
            # Parse task
            result[self.TASK] = split_str[1].strip()

        if (len(split_str) >= 3):
            # Parse project
            result[self.PROJECT] = split_str[2].strip()

        return result

    def group_by_project(self):
        """
        Group tasks by project
        """
        self.one_day_projects = {}
        for i in range(len(self.one_day)):
            if not self.TASK in self.one_day[i]:
                break

            project = ""
            if self.PROJECT in self.one_day[i]:
                project = self.one_day[i][self.PROJECT]
            else:
                project = self.DEFAULT_PROJECT

            if not project in self.one_day_projects:
                self.one_day_projects[project] = {}

            delta_time = (self.one_day[i + 1][self.TIME] -
                          self.one_day[i][self.TIME])

            task = self.one_day[i][self.TASK]
            if not task in self.config.skip_tasks:
                if task in self.one_day_projects[project].keys():
                    self.one_day_projects[project][task] += delta_time
                else:
                    self.one_day_projects[project][task] = delta_time

        # Transform resulting time
        self.transform_time()

    def transform_time(self):
        """
        Transform time [hours]:[minutes]:[seconds] to [hours].[minutes relative]
        """
        result = ""
        for project in self.one_day_projects:
            for task in self.one_day_projects[project]:
                time_str = str(self.one_day_projects[project][task])
                time_arr = time_str.split(":")
                time_arr = self.translate(int(time_arr[0]), int(time_arr[1]))
                self.one_day_projects[project][task] = str(time_arr[0]) + "." + \
                    str(time_arr[1])

    def translate(self, hours, minutes):
        left_min = 0
        left_max = 60
        right_min = 0
        right_max = 100

        left_span = left_max - left_min
        right_span = right_max - right_min

        valueScaled = float(minutes - left_min) / float(left_span)

        minutes = right_min + (valueScaled * right_span)

        # Fractional part rounded to 25
        frac = minutes % 25
        if frac > 0 and frac >= 13:
            minutes = (minutes // 25 + 1) * 25
            if minutes == 100:
                hours += 1
                minutes = 0
        else:
            minutes = minutes // 25 * 25

        return [int(hours), int(minutes)]


if __name__ == "__main__":
    print("Run main app.py file")
