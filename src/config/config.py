#!/usr/bin/python3
"""
Read config file and take config data
"""
import json
from os import path

import dateutil.parser

from ..print_objects import PrintConsole, PrintToFile

# Parameters from file
input_file_hours = ""
output_file_day = ""
skip_tasks = []
outputs_day_report = []
file_type_print = 1
console_type_print = 1
minute_round_to = 25
use_jira = False
jira = {}

# Parameters for program
work_day_hours = dateutil.parser.parse("08:00")


def load_config():
    """
    Parse config file and set settings
    """
    config_file = _get_config_file()

    global input_file_hours
    global output_file_day
    global skip_tasks
    global outputs_day_report
    global file_type_print
    global console_type_print
    global minute_round_to
    global use_jira
    global jira

    data = json.load(open(config_file, "r", encoding="utf-8"))

    if "hour-report-path" in data and path.isfile(data["hour-report-path"]):
        input_file_hours = path.normpath(data["hour-report-path"])
    else:
        exit("Input file is not setted in config.")

    if "day-report-path" in data and path.isfile(data["day-report-path"]):
        output_file_day = data["day-report-path"]

    if "omit-task" in data:
        skip_tasks = data["omit-task"]

    if "outputs-day-report" in data:
        if "console" in data["outputs-day-report"]:
            if 1 <= data["outputs-day-report"]["console"] and data["outputs-day-report"]["console"] <= 2:
                console_type_print = data["outputs-day-report"]["console"]
            outputs_day_report.append(PrintConsole())
        if "file" in data["outputs-day-report"] and output_file_day != "":
            if 1 <= data["outputs-day-report"]["file"] and data["outputs-day-report"]["file"] <= 2:
                file_type_print = data["outputs-day-report"]["file"]
            outputs_day_report.append(PrintToFile())
    else:
        outputs_day_report.append(PrintConsole())

    if "minute_round_to" in data and isinstance(data["minute_round_to"], int):
        minute_round_to = int(data["minute_round_to"])

    if "jira" in data:
        if "server" in data["jira"] and "login" in data["jira"] and "password" in data["jira"]:
            jira = data["jira"]
            use_jira = True

        if "issue_key_base" not in data["jira"]:
            jira.update({"issue_key_base": ""})


def _get_config_file() -> str:
    if path.isfile(path.dirname(__file__) + "/../../config.json"):
        return path.dirname(__file__) + "/../../config.json"
    else:
        exit("Config file is not exist.")
