#!/usr/bin/python3
"""
File with class for print report
"""

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
        self.outputFile = open(outputFilePath, "r+", encoding="utf-8")

    def print(self):
        """
        Print to file
        """
        temp = self.outputFile.readlines()
        self.outputFile.seek(0)
        self.outputFile.write(self.text)
        self.outputFile.write("\n\n")
        self.outputFile.writelines(temp)


if __name__ == "__main__":
    print("Run main app.py file")
