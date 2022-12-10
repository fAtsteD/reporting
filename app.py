#!/usr/bin/python3
"""
Begining point of program
"""
import os
import sys

from src.config_app import *
from src.jira import Jira
from src.reporting import *
from src.transform import *


def main():
    """
    Main function for starting program
    """
    load_config()

    day_data = transform.get_day_data()

    # Print data
    for print_object in config.outputs_day_report:
        print_object.print(day_data)

    # Send data to JIRA
    if config.jira.is_use:
        log_work = input("Log work to JIRA? (y/n) ")
        if log_work == "y":
            jira = Jira()
            jira.set_worklog(day_data)

    # Send data to reporting
    if config.reporting.is_use:
        send_to_reporting = input("Send to reporting? (y/n) ")
        if send_to_reporting == "y":
            send_tasks(day_data)


if __name__ == "__main__":
    main()
