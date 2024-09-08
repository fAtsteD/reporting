import re

import jira.client
import jira.exceptions

from config_app import Config
from models.report import Report


def convert_time_to_jira_time(seconds: int) -> str:
    """
    Convert time to the jira type string
    """
    return f"{round((seconds / 60) // 60)}h {round((seconds / 60) % 60)}m"


class Jira:
    """
    Object with required method
    """

    def __init__(self):
        if not Config.jira.is_use:
            exit("Used JIRA module without required settings")

        if isinstance(Config.jira.issue_key_base, list):
            self._bases = Config.jira.issue_key_base
        else:
            self._bases = [Config.jira.issue_key_base]

        self._jira = jira.client.JIRA(server=Config.jira.server, basic_auth=(Config.jira.login, Config.jira.password))

    def set_worklog(self, report: Report):
        """
        Set worklog time to the task
        """
        bases = map(lambda base: "(?:" + re.escape(base) + "[0-9]+)", self._bases)
        regexp_compile = re.compile("^(" + "|".join(bases) + "):.+$")

        for task in report.tasks:
            task_to_jira = regexp_compile.match(task.summary)

            if task_to_jira is not None:
                is_ok = self._set_worklog_to_jira(
                    task_to_jira.group(1), convert_time_to_jira_time(task.logged_rounded())
                )

                if is_ok:
                    print(f"[+] {task}")
                else:
                    print(f"[-] {task}")

        print()

    def _set_worklog_to_jira(self, issue_key: str, time: str) -> bool:
        """
        Set time (already converted to structure for jira) to the jira server for specific key
        """
        try:
            # First request for checking that issue exist
            self._jira.issue(issue_key)
            self._jira.add_worklog(issue_key, time)
        except jira.exceptions.JIRAError:
            return False

        return True
