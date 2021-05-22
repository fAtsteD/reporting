#!/usr/bin/python3
"""
Read config file and take config data
"""
import json
from os import path

from ..print_objects import PrintConsole, PrintToFile
from .class_config import config


def load_config():
    """
    Parse config file and set settings
    """
    config_file = _get_config_file()

    data = json.load(open(config_file, "r", encoding="utf-8"))

    if "hour-report-path" in data and path.isfile(data["hour-report-path"]):
        config.input_file_hours = path.normpath(data["hour-report-path"])
    else:
        exit("Input file is not setted in config.")

    if "day-report-path" in data and path.isfile(data["day-report-path"]):
        config.output_file_day = data["day-report-path"]

    if "omit-task" in data:
        config.skip_tasks = data["omit-task"]

    if "outputs-day-report" in data:
        if "console" in data["outputs-day-report"]:
            if 1 <= data["outputs-day-report"]["console"] and data["outputs-day-report"]["console"] <= 2:
                config.console_type_print = data["outputs-day-report"]["console"]
            config.outputs_day_report.append(PrintConsole())
        if "file" in data["outputs-day-report"] and config.output_file_day != "":
            if 1 <= data["outputs-day-report"]["file"] and data["outputs-day-report"]["file"] <= 2:
                config.file_type_print = data["outputs-day-report"]["file"]
            config.outputs_day_report.append(PrintToFile())
    else:
        config.outputs_day_report.append(PrintConsole())

    if "minute_round_to" in data and isinstance(data["minute_round_to"], int):
        config.minute_round_to = int(data["minute_round_to"])

    if "jira" in data:
        if "server" in data["jira"] and "login" in data["jira"] and "password" in data["jira"]:
            for param in data["jira"]:
                config.jira[param] = data["jira"][param]
            config.jira["use_jira"] = True


def _get_config_file() -> str:
    if path.isfile(path.dirname(__file__) + "/../../config.json"):
        return path.dirname(__file__) + "/../../config.json"
    else:
        exit("Config file is not exist.")