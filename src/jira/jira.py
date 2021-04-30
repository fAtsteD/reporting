import re

from src.helpers.time import *
from src.transform.transform import Transform

from jira import JIRA, JIRAError


class Jira():
    """
    Object with required method
    """

    def __init__(self, config):
        self._config = config

        if not self._config.use_jira:
            exit("Used JIRA module without required settings")

        self._base = config.fira["issue_key_base"]

        jira_options = {
            "server": config.jira["server"]
        }

        self._jira = JIRA(jira_options, basic_auth=(
            config.jira["login"], config.jira["password"]))

    def set_worklog(self, transform: Transform):
        """
        Set worklog time to the task
        """
        regexp_compile = re.compile("^(" + self._base + "[0-9]+):.+$")

        for project in transform.one_day_projects:
            for task_name in transform.one_day_projects[project].keys():
                task_to_jira = regexp_compile.match(task_name)
                if task_to_jira != None:
                    self._set_worklog_to_jira(
                        task_to_jira.group(1), self._convert_time(transform.one_day_projects[project][task_name]))

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

    def _convert_time(self, time: str):
        """
        Convert time to the jira type string
        """

        hours = int(float(time))
        minutes = int(remap(int((float(time) - hours) * 100), 0, 100, 0, 60))

        return str(hours) + "h " + str(minutes) + "m"
