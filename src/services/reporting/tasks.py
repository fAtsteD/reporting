"""
Work with tasks from app
"""

from models.report import Report

from .api import api
from .common import get_api


def send_tasks(report: Report, report_num=0) -> None:
    """
    Send task to the report. Print status each
    """

    api = get_api()

    reporting_reports = api.get_reports(report.date)

    if reporting_reports is None:
        exit(api.last_error)

    reporting_report_id = None
    if len(reporting_reports) > 0:
        reporting_report_id = report[report_num].report["id"]

    reporting_report = api.set_report(report.date, reporting_report_id)

    if reporting_report is None:
        exit(api.last_error)

    for task in report.tasks:
        print_str = ""
        if api.add_task(task, reporting_report):
            print_str += "[+] "
        else:
            print_str += "[-] "

        print(print_str + task.summary + " - " + task.kind)

    api.logout()
