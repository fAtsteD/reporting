import re

import jira.client
import jira.exceptions

from reporting import config
from reporting.database.models import Report
from reporting.services.jira.exceptions import JiraNotConfiguredError
from reporting.services.jira.models import JiraTaskResult, JiraTaskStatus


def convert_time_to_jira_time(seconds: int) -> str:
    return f"{round((seconds / 60) // 60)}h {round((seconds / 60) % 60)}m"


def set_worklog(report: Report) -> list[JiraTaskResult]:
    config_jira = config.jira

    if not config_jira.is_use:
        raise JiraNotConfiguredError("Jira is not configured. Server address, login and password are required")

    jira_client = jira.client.JIRA(server=config_jira.server, basic_auth=(config_jira.login, config_jira.password))
    bases = ("(?:" + re.escape(base) + "[0-9]+)" for base in config_jira.issue_key_bases)
    regexp_compile = re.compile("^(" + "|".join(bases) + "):.+$")
    results: list[JiraTaskResult] = []

    for task in report.tasks:
        task_to_jira = regexp_compile.match(task.summary)

        if task_to_jira is None:
            continue

        issue_key = task_to_jira.group(1)

        try:
            jira_client.issue(issue_key)
            jira_client.add_worklog(issue_key, convert_time_to_jira_time(task.logged_rounded))
            results.append(JiraTaskResult(status=JiraTaskStatus.SENT, task=task))
        except jira.exceptions.JIRAError as error:
            results.append(JiraTaskResult(status=JiraTaskStatus.FAILED, task=task, reason=error.text or ""))

    return results
