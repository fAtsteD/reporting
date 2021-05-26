import datetime
import re

from jira import JIRA, JIRAError

from ..config_app import config
from ..helpers.time import *
from ..transform import DayData


class Jira():
    """
    Object with required method
    """

    def __init__(self):
        if not config.jira.can_use:
            exit("Used JIRA module without required settings")

        self._base = config.jira.issue_key_base

        jira_options = {
            "server": config.jira.server
        }

        self._jira = JIRA(jira_options, basic_auth=(
            config.jira.login, config.jira.password))

    def set_worklog(self, day_data: DayData):
        """
        Set worklog time to the task
        """
        regexp_compile = re.compile("^(" + self._base + "[0-9]+):.+$")

        for task in day_data.tasks:
            task_to_jira = regexp_compile.match(task.name)
            if task_to_jira != None:
                self._set_worklog_to_jira(task_to_jira.group(
                    1), self._convert_time(task.time))

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

        print_str = ""
        if is_accept:
            print_str = "[+] "
        else:
            print_str = "[-] "

        print(print_str + issue_key + " - " + time)

    def _convert_time(self, time: datetime.timedelta):
        """
        Convert time to the jira type string
        """

        return str(time.seconds // 3600) + "h " + str((time.seconds // 60) % 60) + "m"
