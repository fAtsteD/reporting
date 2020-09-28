#!/usr/bin/python3
"""
File with class for print report
"""
import src.Transform


class PrintAbstract():
    """
    Abstract for printing

    Variable:
    - text - resulting string
    """

    def __init__(self, transform: src.Transform):
        """
        docstring
        """
        self.text = ""
        for project in transform.oneDayProjects.keys():
            self.text += project + ":"
            for task in transform.oneDayProjects[project].keys():
                self.text += "  " + \
                    str(transform.oneDayProjects[project]
                        [task]) + " ч. - " + task


if __name__ == "__main__":
    print("Run main app.py file")
