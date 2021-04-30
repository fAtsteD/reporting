#!/usr/bin/python3
"""
Begining point of program
"""
import os
import sys

from src.config.config import Config
from src.jira.jira import Jira
from src.transform.transform import Transform


def main():
    """
    Main function for starting program
    """
    config = Config()

    transform = Transform(config)

    # Pring data
    for print_object in config.outputs_day_report:
        print_object.print(transform)

    # Send data to JIRA
    log_work = input("Log work? (y/n)")
    if log_work == "y":
        jira = Jira(config)
        jira.set_worklog(transform)


if __name__ == "__main__":
    main()
