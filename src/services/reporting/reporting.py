import requests

from models.report import Report

from .api import ReportingApi


class Reporting:
    """
    Service object for work with reporting
    """

    def __init__(self) -> None:
        self._reporting_api = ReportingApi(requests.Session())

        # Before any request for setting session
        if not self._reporting_api.init():
            exit(self._reporting_api.last_error)

        if not self._reporting_api.login():
            exit(self._reporting_api.last_error)

        if not self._reporting_api.init():
            exit(self._reporting_api.last_error)

        if not self._reporting_api.load_categories():
            exit(self._reporting_api.last_error)

        if not self._reporting_api.load_projects():
            exit(self._reporting_api.last_error)

        if not self._reporting_api.load_positions():
            exit(self._reporting_api.last_error)

    def send_tasks(self, report: Report) -> None:
        """
        Send task to the report. Print each status of sending
        """
        reporting_reports = self._reporting_api.get_reports(report.date)

        if reporting_reports is None:
            exit(self._reporting_api.last_error)

        reporting_report_id = None
        if len(reporting_reports) > 0:
            reporting_report_id = reporting_reports[0].get_id()

        reporting_report = self._reporting_api.set_report(
            report.date, reporting_report_id)

        if reporting_report is None:
            exit(self._reporting_api.last_error)

        for task in report.tasks:
            if self._reporting_api.add_task(task, reporting_report):
                print(f"[+] {task}")
            else:
                print(f"[-] {task}")

        print()

    def logout(self) -> None:
        self._reporting_api.logout()
