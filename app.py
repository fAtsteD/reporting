#!/usr/bin/python3
"""
Begining point of program
"""
import os
import sys

from src.config import config
from src.jira import Jira
from src.transform import *


def main():
    """
    Main function for starting program
    """
    config.load_config()
    day_data = transform.get_day_data()

    # Pring data
    for print_object in config.outputs_day_report:
        print_object.print(day_data)

    # # Send data to JIRA
    if config.use_jira:
        log_work = input("Log work? (y/n)")
        if log_work == "y":
            jira = Jira()
            jira.set_worklog(day_data)


if __name__ == "__main__":
    main()
