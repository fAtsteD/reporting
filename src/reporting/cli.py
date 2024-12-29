#!/usr/bin/python3

from datetime import date

from reporting import config_app
from reporting.config_app.class_config import Command
from reporting.models import Kind, Project, Report
from reporting.services import jira
from reporting.services.file_parse import parse_reports
from reporting.services.reporting.actions import send_tasks


def kind_update() -> None:
    config = config_app.config
    kind: Kind | None = config.sqlite_session.query(Kind).filter(Kind.alias == config.kind_data[0]).first()
    if kind is None:
        kind = Kind(alias=config.kind_data[0], name=config.kind_data[1])
        config.sqlite_session.add(kind)
    else:
        kind.name = config.kind_data[1]
    config.sqlite_session.commit()


def kinds_show() -> None:
    config = config_app.config
    kinds = config.sqlite_session.query(Kind).order_by(Kind.name).all()
    print("Kinds:")
    for kind in kinds:
        print(kind)


def project_update() -> None:
    config = config_app.config
    project: Project | None = (
        config.sqlite_session.query(Project).filter(Project.alias == config.project_data[0]).first()
    )
    if project is None:
        project = Project(alias=config.project_data[0], name=config.project_data[1])
        config.sqlite_session.add(project)
    else:
        project.name = config.project_data[1]
    config.sqlite_session.commit()


def projects_show() -> None:
    config = config_app.config
    projects = config.sqlite_session.query(Project).order_by(Project.name).all()
    print("Projects:")
    for project in projects:
        print(project)


def report_parse() -> None:
    config = config_app.config
    reports = parse_reports(config.parse_days or 1)
    print(f"Parsed {len(reports)}")

    if len(reports) < 10:
        for report in reports:
            print(report)


def report_show() -> None:
    config = config_app.config
    report = None

    if config.show_date == "last":
        report = config.sqlite_session.query(Report).order_by(Report.date.desc()).first()
    else:
        report = config.sqlite_session.query(Report).filter(Report.date == config.show_date).first()

    if report is None:
        print("Report does not exist")
    else:
        print(report)


def send_to_jira() -> None:
    config = config_app.config
    report: Report | None = None
    print("Jira")

    if config.jira.report_date == "last":
        report = config.sqlite_session.query(Report).order_by(Report.date.desc()).first()
    else:
        report = config.sqlite_session.query(Report).filter(Report.date == config.jira.report_date).first()

    if report:
        jira.set_worklog(report)


def send_to_reporting() -> None:
    config = config_app.config
    current_date = date.today()
    report = None
    reporting_send_task = "y"
    print("Reporting")

    if config.reporting.report_date == "last":
        report = config.sqlite_session.query(Report).order_by(Report.date.desc()).first()
    else:
        report = config.sqlite_session.query(Report).filter(Report.date == config.reporting.report_date).first()

    if report:
        if (current_date - report.date).days > config.reporting.safe_send_report_days:
            print(f"Report date: {report.date.strftime('%d.%m.%Y')}\Current date: {current_date.strftime('%d.%m.%Y')}")
            reporting_send_task = input(
                f"The date difference more than {config.reporting.safe_send_report_days} day(s). Do you want send tasks? (y/n) "
            )

        if reporting_send_task == "y":
            send_tasks(report)


def main(cli_args: list[str] | None = None) -> None:
    """
    Main function for starting program
    """
    config_app.load_config(cli_args)
    config = config_app.config

    for command in config.commands:
        match command:
            case Command.JIRA:
                send_to_jira()
            case Command.KIND_SHOW:
                kinds_show()
            case Command.KIND_UPDATE:
                kind_update()
            case Command.PROJECT_SHOW:
                projects_show()
            case Command.PROJECT_UPDATE:
                project_update()
            case Command.REPORT_PARSE:
                report_parse()
            case Command.REPORT_SHOW:
                report_show()
            case Command.REPORTING:
                send_to_reporting()


if __name__ == "__main__":
    main()
