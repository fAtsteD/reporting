#!/usr/bin/python3
"""
Begining point of program
"""

from config_app import config, load_config
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

    if config.kind_data:
        kind_service = KindService()
        kind_service.add(config.kind_data[0], config.kind_data[1])
        config.show_kinds = True

    if config.show_kinds:
        kind_service = KindService()
        print("Kinds:")
        print(kind_service.text_all_kinds())

    if config.project_data:
        project_service = ProjectService()
        project_service.add(config.project_data[0], config.project_data[1])
        config.show_projects = True

    if config.show_projects:
        project_service = ProjectService()
        print("Projects:")
        print(project_service.text_all_projects())

    if config.parse_days is not None:
        file_parse = FileParse(config.input_file_hours, config.parse_days)
        reports = file_parse.reports()

        for report in reports:
            print(report)

    if config.show_date is not None:
        report = None

        if config.show_date == 'last':
            report = config.sqlite_session.query(
                Report
            ).order_by(
                Report.date.desc()
            ).first()
        else:
            report = config.sqlite_session.query(
                Report
            ).filter(
                Report.date == config.show_date
            ).first()

        if report is None:
            print(f"Report does not exist")
        else:
            print(report)

    if config.jira.is_use:
        report = None

        if config.jira.report_date == 'last':
            report = config.sqlite_session.query(
                Report
            ).order_by(
                Report.date.desc()
            ).first()
        else:
            report = config.sqlite_session.query(
                Report
            ).filter(
                Report.date == config.jira.report_date
            ).first()

        jira = Jira()
        jira.set_worklog(report)

    if config.reporting.is_use:
        report = None

        if config.reporting.report_date == 'last':
            report = config.sqlite_session.query(
                Report
            ).order_by(
                Report.date.desc()
            ).first()
        else:
            report = config.sqlite_session.query(
                Report
            ).filter(
                Report.date == config.reporting.report_date
            ).first()

        reporting = Reporting()
        reporting.send_tasks(report)
        reporting.logout()


if __name__ == "__main__":
    main()
