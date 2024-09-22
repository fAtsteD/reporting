import argparse
import json
import os
import re
from pathlib import Path

import dateutil.parser

from reporting.config_app.class_config import Command, Config
from reporting.config_app.dictionary import Dictionary
from reporting.config_app.jira_config import JiraConfig
from reporting.config_app.reporting_config import ReportingConfig

__all__ = ["config", "load_config"]

config: Config = Config()


def load_config(cli_args: list[str] | None = None):
    """
    Parse config file and set settings
    """
    global config
    config = Config()
    config_file = Path(config.program_dir, "config.json").expanduser()
    config_file.parent.mkdir(parents=True, exist_ok=True)

    if not config_file.is_file():
        exit(f"Config file is not exist. Create configuration in {config_file}")

    data = json.load(config_file.open("r", encoding="utf-8"))

    if "default-project" in data:
        config.default_project = data["default-project"]
    if "default-type" in data:
        config.default_kind = data["default-type"]
    if "dictionary" in data:
        dictionary_dict = {}
        if "task" in data["dictionary"]:
            dictionary_dict["tasks"] = data["dictionary"]["task"]
        if "type" in data["dictionary"]:
            dictionary_dict["kinds"] = data["dictionary"]["type"]
        if "project" in data["dictionary"]:
            dictionary_dict["projects"] = data["dictionary"]["project"]
        config.dictionary = Dictionary(**dictionary_dict)
    if "hour-report-path" in data and os.path.isfile(data["hour-report-path"]):
        config.input_file_hours = os.path.normpath(data["hour-report-path"])
    if "minute-round-to" in data and isinstance(data["minute-round-to"], int):
        config.minute_round_to = int(data["minute-round-to"])
    if "omit-task" in data:
        skip_tasks = data["omit-task"]
        for task_name in skip_tasks:
            config.skip_tasks.append(config.dictionary.translate_task(task_name))
    if "sqlite-database-path" in data:
        config.sqlite_database_path = os.path.normpath(data["sqlite-database-path"])

    if "jira" in data:
        config.jira = JiraConfig(
            issue_key_bases=data["jira"]["issue-key-base"] if "issue-key-base" in data["jira"] else [],
            login=data["jira"]["login"] if "login" in data["jira"] else "",
            password=data["jira"]["password"] if "password" in data["jira"] else "",
            server=data["jira"]["server"] if "server" in data["jira"] else "",
        )

    if "reporting" in data:
        reporting_dict = {}
        if "project-to-corp-struct-item" in data["reporting"]:
            reporting_dict["project_to_corp_struct_item"] = data["reporting"]["project-to-corp-struct-item"]
        config.reporting = ReportingConfig(
            safe_send_report_days=(
                data["reporting"]["safe-send-report-days"]
                if "safe-send-report-days" in data["reporting"] and data["reporting"]["safe-send-report-days"] > 0
                else 0
            ),
            kinds=data["reporting"]["kinds"] if "kinds" in data["reporting"] else {},
            login=data["reporting"]["login"] if "login" in data["reporting"] else "",
            password=data["reporting"]["password"] if "password" in data["reporting"] else "",
            projects=data["reporting"]["projects"] if "projects" in data["reporting"] else {},
            project_to_corp_struct_item=(
                data["reporting"]["project-to-corp-struct-item"]
                if "project-to-corp-struct-item" in data["reporting"]
                else {}
            ),
            url=data["reporting"]["url"] if "url" in data["reporting"] else "",
        )

    _config_arguments(cli_args)


def _config_arguments(cli_args: list[str] | None):
    """
    Parse params from arguments to program
    """
    global config
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
        "--show-kinds",
        required=False,
        default=False,
        action="store_true",
        help="print all kinds and their data",
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
        "--show-projects",
        required=False,
        default=False,
        action="store_true",
        help="print all projects and their data",
    )

    args = parser.parse_args(cli_args)

    regex_date = "^[0-9]{1,2}\\.[0-9]{1,2}\\.([0-9]{4}|[0-9]{2})$"

    if args.show is not None:
        config.commands.append(Command.REPORT_SHOW)
        if re.search(regex_date, args.show.strip()):
            config.show_date = dateutil.parser.parse(args.show, dayfirst=True).date()

    if args.parse is not None and int(args.parse) >= 0:
        config.commands.append(Command.REPORT_PARSE)
        config.parse_days = int(args.parse)

    if args.jira is not None:
        config.commands.append(Command.JIRA)
        if re.search(regex_date, args.jira.strip()):
            config.jira.report_date = dateutil.parser.parse(args.jira, dayfirst=True).date()

    if args.reporting is not None:
        config.commands.append(Command.REPORTING)
        if re.search(regex_date, args.reporting.strip()):
            config.reporting.report_date = dateutil.parser.parse(args.reporting, dayfirst=True).date()

    if args.kind:
        config.commands.append(Command.KIND_UPDATE)
        config.commands.append(Command.KIND_SHOW)
        config.kind_data = args.kind

    if args.show_kinds:
        config.commands.append(Command.KIND_SHOW)

    if args.project:
        config.commands.append(Command.PROJECT_UPDATE)
        config.commands.append(Command.PROJECT_SHOW)
        config.project_data = args.project

    if args.show_projects:
        config.commands.append(Command.PROJECT_SHOW)
