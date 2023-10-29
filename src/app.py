#!/usr/bin/python3
"""
Begining point of program
"""

from config_app import Config, load_config
from models.report import Report
from services.file_parse import FileParse
from services.jira import Jira
from services.kind import KindService
from services.project import ProjectService
from services.reporting import Reporting


def main():
    """
    Main function for starting program
    """
    load_config()

    if Config.kind_data:
        kind_service = KindService()
        kind_service.add(Config.kind_data[0], Config.kind_data[1])
        Config.show_kinds = True

    if Config.show_kinds:
        kind_service = KindService()
        print("Kinds:")
        print(kind_service.text_all_kinds())

    if Config.project_data:
        project_service = ProjectService()
        project_service.add(Config.project_data[0], Config.project_data[1])
        Config.show_projects = True

    if Config.show_projects:
        project_service = ProjectService()
        print("Projects:")
        print(project_service.text_all_projects())

    if Config.parse_days is not None:
        file_parse = FileParse(Config.input_file_hours, Config.parse_days)
        reports = file_parse.reports()
        print(f"Parsed {len(reports)}")

        if len(reports) < 10:
            for report in reports:
                print(report)

    if Config.show_date is not None:
        report = None

        if Config.show_date == 'last':
            report = Config.sqlite_session.query(
                Report
            ).order_by(
                Report.date.desc()
            ).first()
        else:
            report = Config.sqlite_session.query(
                Report
            ).filter(
                Report.date == Config.show_date
            ).first()

        if report is None:
            print(f"Report does not exist")
        else:
            print(report)

    if Config.jira.is_use:
        report = None
        print("Jira")

        if Config.jira.report_date == 'last':
            report = Config.sqlite_session.query(
                Report
            ).order_by(
                Report.date.desc()
            ).first()
        else:
            report = Config.sqlite_session.query(
                Report
            ).filter(
                Report.date == Config.jira.report_date
            ).first()

        jira = Jira()
        jira.set_worklog(report)

    if Config.reporting.is_use:
        report = None
        print("Reporting")

        if Config.reporting.report_date == 'last':
            report = Config.sqlite_session.query(
                Report
            ).order_by(
                Report.date.desc()
            ).first()
        else:
            report = Config.sqlite_session.query(
                Report
            ).filter(
                Report.date == Config.reporting.report_date
            ).first()

        reporting = Reporting()
        reporting.send_tasks(report)
        reporting.logout()


if __name__ == "__main__":
    main()
