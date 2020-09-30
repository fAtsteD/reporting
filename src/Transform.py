#!/usr/bin/python3

"""
File with class for transform hours to daily report
"""

import codecs
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

    Variables:
    - inputFileHours - input file tasks by hours
    - date - date of report from input file
    - oneDay - array with dictionary task by hours
    - oneDayProjects - dictionaty with task by projects and sum of time for each task
    """
    SKIP_TASK = [
        "обед",
        "перерыв"
    ]

    TIME = "time"
    TASK = "task"
    PROJECT = "project"

    DEFAULT_PROJECT = "Внутренние задачи"

    def __init__(self, inputFile):
        if inputFile is None:
            exit("Must have input argument.")
        self.inputFileHours = codecs.open(inputFile, "r", "utf_8_sig")

        self.readOneDay()
        self.groupByProject()

    def readOneDay(self):
        """
        Read all tasks for one day to array
        """
        self.oneDay = []
        # Need for double new line finding
        previousLine = ""
        for line in self.inputFileHours:
            if (re.search("^[0-9]{1,2}\.[0-9]{1,2}\.([0-9]{4}|[0-9]{2})\n$", line)):
                self.date = dateutil.parser.parse(line)
                continue

            if previousLine == "\n" and line == "\n":
                break
            else:
                previousLine = line

            if line == "\n":
                continue

            self.oneDay.append(self.parseTask(line))

    def parseTask(self, taskStr: str):
        """
        Parse string to array of date, name of task, name of project

        Returning dictionary
        """
        result = {}

        splitStr = taskStr.split(" - ")

        if (len(splitStr) >= 1):
            # Parse time, date will be cuurent, it is not right
            result[self.TIME] = dateutil.parser.parse(
                splitStr[0].replace(" ", ":").strip())

        if (len(splitStr) >= 2):
            # Parse task
            result[self.TASK] = splitStr[1].strip()

        if (len(splitStr) >= 3):
            # Parse project
            result[self.PROJECT] = splitStr[2].strip()

        return result

    def groupByProject(self):
        """
        Group tasks by project
        """
        self.oneDayProjects = {}
        for i in range(len(self.oneDay)):
            if not self.TASK in self.oneDay[i]:
                break

            project = ""
            if self.PROJECT in self.oneDay[i]:
                project = self.oneDay[i][self.PROJECT]
            else:
                project = self.DEFAULT_PROJECT

            if not project in self.oneDayProjects:
                self.oneDayProjects[project] = {}

            deltaTime = (self.oneDay[i + 1][self.TIME] -
                         self.oneDay[i][self.TIME])

            task = self.oneDay[i][self.TASK]
            if not task in self.SKIP_TASK:
                if task in self.oneDayProjects[project].keys():
                    self.oneDayProjects[project][task] += deltaTime
                else:
                    self.oneDayProjects[project][task] = deltaTime

        # Transform resulting time
        self.transformTime()

    def transformTime(self):
        """
        Transform time [hours]:[minutes]:[seconds] to [hours].[minutes relative]
        """
        result = ""
        for project in self.oneDayProjects:
            for task in self.oneDayProjects[project]:
                timeStr = str(self.oneDayProjects[project][task])
                timeArr = timeStr.split(":")
                self.oneDayProjects[project][task] = timeArr[0] + "." + \
                    str(int(self.translate(int(timeArr[1]), 0, 60, 0, 100)))

    def translate(self, value, leftMin, leftMax, rightMin, rightMax):
        leftSpan = leftMax - leftMin
        rightSpan = rightMax - rightMin

        valueScaled = float(value - leftMin) / float(leftSpan)

        translated = rightMin + (valueScaled * rightSpan)

        # Fractional part rounded to 25
        frac = translated % 25
        if frac > 0 and frac >= 13:
            translated = (translated // 25 + 1) * 25
        else:
            translated = translated // 25 * 25

        return translated


if __name__ == "__main__":
    print("Run main app.py file")
