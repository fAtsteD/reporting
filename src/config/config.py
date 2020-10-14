#!/usr/bin/python3
"""
Read config file and take config data
"""
import json
from os import path

import dateutil.parser
from src.print_objects.print_console import PrintConsole
from src.print_objects.print_to_file import PrintToFile


class Config():
    """
    Config data class

    Properties:
    - input_file_hours - path to file with tasks by hours
    - output_file_day - path to file with summary tasks by project for one day
    - skip_tasks - array of skipped tasks
    - outputs_day_report - where print day report ["console", "file"]
    """

    # Parameters from file
    input_file_hours = ""
    output_file_day = ""
    skip_tasks = []
    outputs_day_report = []

    # Parameters for program
    work_day_hours = dateutil.parser.parse("08:00")

    def __init__(self):
        file_path = path.normpath(path.dirname(
            __file__) + "/../../config.json")
        if path.isfile(path.normpath(path.dirname(__file__) + "/../../config.json")):
            self.config_file = path.normpath(
                path.dirname(__file__) + "/../../config.json")
        else:
            print("Config file is not found.")
            exit()

        self.parse_config()

    def parse_config(self):
        """
        Parse config file and save settings
        """
        data = json.load(open(self.config_file, "r", encoding="utf-8"))

        if "hour-report-path" in data and data["hour-report-path"] != "":
            self.input_file_hours = path.realpath(path.normpath(
                data["hour-report-path"]))
        else:
            print("Input file is not setted in config.")
            exit()

        if "day-report-path" in data["day-report-path"] != "":
            self.output_file_day = path.realpath(
                path.normpath(data["day-report-path"]))

        if "omit-task" in data:
            self.skip_tasks = data["omit-task"]

        if "output-day-report" in data:
            if "console" in data["output-day-report"]:
                self.outputs_day_report.append(
                    PrintConsole())
            if "file" in data["output-day-report"] and self.output_file_day != "":
                self.outputs_day_report.append(
                    PrintToFile(self.output_file_day))
        else:
            self.outputs_day_report.append(
                PrintConsole())


if __name__ == "__main__":
    print("Run main app.py file")
