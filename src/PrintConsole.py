#!/usr/bin/python3
"""
File with class for print report
"""

from src.PrintAbstract import PrintAbstract


class PrintConsole(PrintAbstract):
    """
    Print result to console
    """

    def print(self):
        """
        Print to console
        """
        print(self.text)


if __name__ == "__main__":
    print("Run main app.py file")
