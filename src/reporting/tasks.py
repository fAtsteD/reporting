"""
Work with tasks from app
"""
from ..transform import DayData
from .api import *
from .common import get_api


def send_tasks(day_data: DayData) -> None:
    """
    Send task to the report. Print status each
    """
    api = get_api()

    reports = api.get_reports(day_data.date)

    if reports is None:
        exit(api.last_error)

    if len(reports) == 0:
        report = api.set_report(day_data.date)

        if report is None:
            exit(api.last_error)

        reports.append(report)

    for task in day_data.tasks:
        print_str = ""
        if api.add_task(task, reports[0]):
            print_str += "[+] "
        else:
            print_str += "[-] "
        print(print_str + task.name + " - " + task.kind)
