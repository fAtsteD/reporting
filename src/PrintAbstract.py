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
        """
        docstring
        """
        self.text = ""
        for project in transform.oneDayProjects.keys():
            self.text += project + ":" + "\n"
            for task in transform.oneDayProjects[project].keys():
                self.text += "  " + \
                    str(transform.oneDayProjects[project]
                        [task]) + " ч. - " + task + "\n"


if __name__ == "__main__":
    print("Run main app.py file")
