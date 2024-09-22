import re

import jira.client
import jira.exceptions

import config_app
from models.report import Report


def set_worklog(report: Report) -> None:
    """
    Set worklog time to the task
    """
    config_jira = config_app.config.jira

    if not config_jira.is_use:
        return

    jira_client = jira.client.JIRA(server=config_jira.server, basic_auth=(config_jira.login, config_jira.password))
    bases = map(lambda base: "(?:" + re.escape(base) + "[0-9]+)", config_jira.issue_key_bases)
    regexp_compile = re.compile("^(" + "|".join(bases) + "):.+$")

    for task in report.tasks:
        task_to_jira = regexp_compile.match(task.summary)

        if task_to_jira is not None:
            issue_key = task_to_jira.group(1)

            try:
                # First request for checking that issue exist
                jira_client.issue(issue_key)
                jira_client.add_worklog(
                    issue_key,
                    convert_time_to_jira_time(task.logged_rounded()),
                )
                print(f"[+] {task}")
            except jira.exceptions.JIRAError:
                print(f"[-] {task}")

    print()


def convert_time_to_jira_time(seconds: int) -> str:
    """
    Convert time to the jira type string
    """
    return f"{round((seconds / 60) // 60)}h {round((seconds / 60) % 60)}m"
