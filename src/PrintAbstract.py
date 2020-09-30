#!/usr/bin/python3
"""
File with class for print report
"""
from src.Transform import Transform


class PrintAbstract():
    """
    Abstract for printing

    Variable:
    - text - resulting string
    """

    def __init__(self, transform: Transform):
        self.text = transform.date.strftime("%d.%m.%Y") + "\n"
        self.text += "Задачи за сегодня:\n"
        for project in transform.oneDayProjects.keys():
            textTasks = ""
            projectTime = 0.0
            for task in transform.oneDayProjects[project].keys():
                projectTime += float(transform.oneDayProjects[project][task])
                textTasks += "    " + \
                    transform.oneDayProjects[project][task] + \
                    " ч. - " + task + "\n"

            self.text += "  " + project + \
                "(" + str(projectTime) + " ч.):" + "\n"
            self.text += textTasks


if __name__ == "__main__":
    print("Run main app.py file")
