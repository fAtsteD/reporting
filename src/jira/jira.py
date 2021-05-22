import datetime
import re

from jira import JIRA, JIRAError

from ..helpers.time import *
from ..transform import DayData


class Jira():
    """
    Object with required method
    """

    def __init__(self, config):

        if not config["use_jira"]:
            exit("Used JIRA module without required settings")

        self._base = config["issue_key_base"]

        jira_options = {
            "server": config["server"]
        }

        self._jira = JIRA(jira_options, basic_auth=(
            config["login"], config["password"]))

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

        if is_accept:
            print("[+] " + issue_key + " - " + time)
        else:
            print("[-] " + issue_key + " - " + time)

    def _convert_time(self, time: datetime.datetime):
        """
        Convert time to the jira type string
        """

        return str(time.hour) + "h " + str(time.hour) + "m"
