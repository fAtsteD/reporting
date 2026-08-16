import json
import os
import sys
from pathlib import Path

from reporting.config.app import AppConfig
from reporting.config.dictionary import Dictionary
from reporting.config.jira import JiraConfig
from reporting.config.qatestlab_portal import QATestLabPortalConfig
from reporting.database import db_connection

app: AppConfig = AppConfig()
dictionary = Dictionary()
jira = JiraConfig()
qatestlab_portal = QATestLabPortalConfig()


def load_config() -> None:
    global app, dictionary, jira, qatestlab_portal
    app = AppConfig()
    config_file = Path(app.program_dir, "config.json").expanduser()
    config_file.parent.mkdir(parents=True, exist_ok=True)

    if not config_file.is_file():
        sys.exit(f"Config file is not exist. Create configuration in {config_file}")

    data = json.load(config_file.open("r", encoding="utf-8"))

    if "default-project" in data:
        app.default_project = data["default-project"]
    if "default-type" in data:
        app.default_kind = data["default-type"]
    if "dictionary" in data:
        dictionary_dict = {}
        if "project" in data["dictionary"]:
            dictionary_dict["projects"] = data["dictionary"]["project"]
        if "task" in data["dictionary"]:
            dictionary_dict["tasks"] = data["dictionary"]["task"]
        if "type" in data["dictionary"]:
            dictionary_dict["kinds"] = data["dictionary"]["type"]
        dictionary = Dictionary(**dictionary_dict)
    if "hour-report-path" in data and os.path.isfile(data["hour-report-path"]):
        app.input_file_hours = os.path.normpath(data["hour-report-path"])
    if "timezone" in data:
        app.timezone_name = data["timezone"]
    if "jira" in data:
        jira = JiraConfig(
            issue_key_bases=data["jira"].get("issue-key-base", []),
            login=data["jira"].get("login", ""),
            password=data["jira"].get("password", ""),
            server=data["jira"].get("server", ""),
        )
    if "minute-round-to" in data and isinstance(data["minute-round-to"], int):
        app.minute_round_to = int(data["minute-round-to"])
    if "omit-task" in data:
        skip_tasks = data["omit-task"]
        for task_name in skip_tasks:
            app.skip_tasks.append(dictionary.translate_task(task_name))
    if "qatestlab-portal" in data:
        qatestlab_portal_dict = {}
        if "project-to-corp-struct-item" in data["qatestlab-portal"]:
            qatestlab_portal_dict["project_to_corp_struct_item"] = data["qatestlab-portal"][
                "project-to-corp-struct-item"
            ]
        qatestlab_portal = QATestLabPortalConfig(
            kinds=data["qatestlab-portal"].get("kinds", {}),
            login=data["qatestlab-portal"].get("login", ""),
            password=data["qatestlab-portal"].get("password", ""),
            projects=data["qatestlab-portal"].get("projects", {}),
            project_to_corp_struct_item=(data["qatestlab-portal"].get("project-to-corp-struct-item", {})),
            safe_send_report_days=(
                data["qatestlab-portal"]["safe-send-report-days"]
                if "safe-send-report-days" in data["qatestlab-portal"]
                and data["qatestlab-portal"]["safe-send-report-days"] > 0
                else 0
            ),
            url=data["qatestlab-portal"].get("url", ""),
        )
    if "sqlite-database-path" in data:
        db_connection.reconnect(os.path.normpath(data["sqlite-database-path"]))
