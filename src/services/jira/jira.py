import datetime
import re

from jira import JIRA, JIRAError

from config_app import config
from models.report import Report


class Jira():
    """
    Object with required method
    """

    def __init__(self):
        if not config.jira.is_use:
            exit("Used JIRA module without required settings")

        if isinstance(config.jira.issue_key_base, list):
            self._bases = config.jira.issue_key_base
        else:
            self._bases = [config.jira.issue_key_base]

        jira_options = {
            "server": config.jira.server
        }

        self._jira = JIRA(jira_options, basic_auth=(
            config.jira.login, config.jira.password))

    def set_worklog(self, report: Report):
        """
        Set worklog time to the task
        """
        bases = map(
            lambda base: '(?:' + re.escape(base) + '[0-9]+)', self._bases)
        regexp_compile = re.compile("^(" + '|'.join(bases) + "):.+$")

        for task in report.tasks:
            task_to_jira = regexp_compile.match(task.summary)

            if task_to_jira != None:
                self._set_worklog_to_jira(
                    task_to_jira.group(1),
                    self._convert_time(task.logged_rounded())
                )

    def _set_worklog_to_jira(self, issue_key: str, time: str):
        """
        Set time (already converted to structure for jira) to the jira server for specific key
        """
        is_accept = True

        try:
            issue = self._jira.issue(issue_key)
            worklog = self._jira.add_worklog(issue_key, time)
        except JIRAError:
            is_accept = False

        if is_accept:
            print(f"[+] {issue_key} - {time}")
        else:
            print(f"[-] {issue_key} - {time}")

    def _convert_time(self, seconds: int) -> str:
        """
        Convert time to the jira type string
        """

        return str(seconds // 3600) + "h " + str((seconds // 60) % 60) + "m"
