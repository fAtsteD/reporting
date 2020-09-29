#!/usr/bin/python3
"""
File with class for print report
"""

import codecs

from src.PrintAbstract import PrintAbstract
from src.Transform import Transform


class PrintToFile(PrintAbstract):
    """
    Print result report to file, default name of file "report.txt"

    Variables:
    - outputFile - file for printing result
    """

    def __init__(self, transform: Transform, outputFilePath="report.txt"):
        super(PrintToFile, self).__init__(transform)
        self.outputFile = codecs.open(outputFilePath, "a", "utf_8_sig")

    def print(self):
        """
        Print to file
        """
        self.outputFile.write(self.text)
        self.outputFile.write("\n\n")


if __name__ == "__main__":
    print("Run main app.py file")
