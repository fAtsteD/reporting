#!/usr/bin/python3
"""
File with class for print report
"""
from src.transform.transform import Transform


class PrintAbstract():
    """
    Abstract for printing

    Variable:
    - text - resulting string
    """

    def _parse_for_plain_print(self, transform: Transform):
        """
        Parse data for printing
        """
        day_time = 0.0
        text_projects = "Задачи за сегодня:\n"
        text_default_project = ""
        for project in transform.one_day_projects.keys():
            text_tasks = ""
            project_time = 0.0
            for task in transform.one_day_projects[project].keys():
                project_time += float(
                    transform.one_day_projects[project][task])
                text_tasks += "    " + \
                    transform.one_day_projects[project][task] + \
                    " ч. - " + task + "\n"

            if project == transform.DEFAULT_PROJECT:
                text_default_project += "  " + project + \
                    " (" + str(project_time) + " ч.):" + "\n"
                text_default_project += text_tasks
            else:
                text_projects += "  " + project + \
                    " (" + str(project_time) + " ч.):" + "\n"
                text_projects += text_tasks

            day_time += project_time

        text_projects += text_default_project

        self.text = transform.date.strftime("%d.%m.%Y") + "\n"
        self.text += "За день было отработано: " + str(day_time) + " ч.\n"
        self.text += text_projects


if __name__ == "__main__":
    print("Run main app.py file")
