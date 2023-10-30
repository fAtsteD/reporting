"""
Read config file and take config data
"""
import argparse
import json
import re
from os import makedirs, path

import dateutil.parser
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models.base import Base

from .class_config import Config


def load_config():
    """
    Parse config file and set settings
    """
    if path.isfile(path.dirname(__file__) + "/../../config.json"):
        config_file = path.dirname(__file__) + "/../../config.json"
    else:
        exit("Config file is not exist.")

    data = json.load(open(config_file, "r", encoding="utf-8"))

    if "hour-report-path" in data and path.isfile(data["hour-report-path"]):
        Config.input_file_hours = path.normpath(data["hour-report-path"])

    if "sqlite-database-path" in data:
        Config.sqlite_database_path = path.normpath(data["sqlite-database-path"])

        if not path.exists(path.dirname(Config.sqlite_database_path)):
            makedirs(path.dirname(Config.sqlite_database_path))

    if "dictionary" in data:
        Config.dictionary.set_data(data["dictionary"])

    if "default-type" in data:
        Config.default_kind = data["default-type"]

    if "default-project" in data:
        Config.default_project = data["default-project"]

    if "omit-task" in data:
        skip_tasks = data["omit-task"]
        for task_name in skip_tasks:
            Config.skip_tasks.append(Config.dictionary.translate_task(task_name))

    if "minute-round-to" in data and isinstance(data["minute-round-to"], int):
        Config.minute_round_to = int(data["minute-round-to"])

    if "jira" in data:
        Config.jira.set_data(data["jira"])

    if "indent" in data:
        Config.text_indent = data["indent"]

    if "reporting" in data:
        Config.reporting.set_data(data["reporting"])

    _config_arguments()
    _sqlaclchemy_init()


def _config_arguments():
    """
    Parse params from arguments to program
    """
    parser = argparse.ArgumentParser(
        description="Parse file with day (days) of tasks begins in some time and save it is in many systems"
    )

    parser.add_argument(
        "--show",
        required=False,
        nargs="?",
        const="last",
        metavar="01.01.2000",
        action="store",
        help="print report for defined date or last by default",
    )
    parser.add_argument(
        "--parse",
        required=False,
        nargs="?",
        const=1,
        metavar="N",
        action="store",
        help="parse last n days from file and save to db, default 1, set 0 for all report in file",
    )
    parser.add_argument(
        "--jira",
        required=False,
        nargs="?",
        const="last",
        metavar="01.01.2000",
        action="store",
        help="search task from Jira and logs time to them, default for last report",
    )
    parser.add_argument(
        "--reporting",
        required=False,
        nargs="?",
        const="last",
        metavar="01.01.2000",
        action="store",
        help="log all task time to the reporting system, default for last report",
    )

    parser.add_argument(
        "--kind",
        required=False,
        nargs=2,
        metavar=("t", "Test"),
        action="store",
        help="add/update kind to the database and can be used in the future, alias (first param) is "
        "unique, other data will updates",
    )
    parser.add_argument(
        "--show-kinds", required=False, default=False, action="store_true", help="print all kinds and their data"
    )

    parser.add_argument(
        "--project",
        required=False,
        nargs=2,
        metavar=("p", "Project"),
        action="store",
        help="add/update project to the database and can be used in the future, alias (first param) "
        "is unique, other data will updates",
    )
    parser.add_argument(
        "--show-projects", required=False, default=False, action="store_true", help="print all projects and their data"
    )

    args = parser.parse_args()

    regex_date = "^[0-9]{1,2}\\.[0-9]{1,2}\\.([0-9]{4}|[0-9]{2})$"

    if args.show is not None:
        if re.search(regex_date, args.show.strip()):
            Config.show_date = dateutil.parser.parse(args.show, dayfirst=True).date()
        else:
            Config.show_date = args.show

    if args.parse is not None and int(args.parse) >= 0:
        Config.parse_days = int(args.parse)

    if args.jira is not None:
        Config.jira.is_use = True if Config.jira.is_use else Config.jira.is_use

        if re.search(regex_date, args.jira.strip()):
            Config.jira.report_date = dateutil.parser.parse(args.jira, dayfirst=True).date()
    else:
        Config.jira.is_use = False

    if args.reporting is not None:
        Config.reporting.is_use = True if Config.reporting.is_use else Config.reporting.is_use

        if re.search(regex_date, args.reporting.strip()):
            Config.reporting.report_date = dateutil.parser.parse(args.reporting, dayfirst=True).date()
    else:
        Config.reporting.is_use = False

    if args.kind:
        Config.kind_data = args.kind

    Config.show_kinds = args.show_kinds

    if args.project:
        Config.project_data = args.project

    Config.show_projects = args.show_projects


def _sqlaclchemy_init():
    """
    Initialize SQLAlchemy library and migrate
    """
    sqlalchemy_engine = create_engine("sqlite:///" + Config.sqlite_database_path, echo=False, future=True)
    Session = sessionmaker(bind=sqlalchemy_engine)
    Config.sqlite_session = Session()

    Base.metadata.create_all(sqlalchemy_engine)
