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
        dayTime = 0.0
        textProjects = "Задачи за сегодня:\n"
        for project in transform.oneDayProjects.keys():
            textTasks = ""
            projectTime = 0.0
            for task in transform.oneDayProjects[project].keys():
                projectTime += float(transform.oneDayProjects[project][task])
                textTasks += "    " + \
                    transform.oneDayProjects[project][task] + \
                    " ч. - " + task + "\n"

            textProjects += "  " + project + \
                "(" + str(projectTime) + " ч.):" + "\n"
            textProjects += textTasks

            dayTime += projectTime

        self.text = transform.date.strftime("%d.%m.%Y") + "\n"
        self.text += "За день было отработано: " + str(dayTime) + " ч.\n"
        self.text += textProjects


if __name__ == "__main__":
    print("Run main app.py file")
