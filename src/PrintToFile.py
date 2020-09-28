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
        self.outputFile = codecs.open(outputFilePath, "r+", "utf_8_sig")
        #self.outputFile.seek(0, 0)

    def __del__(self):
        self.outputFile.close()

    def print(self):
        """
        Print to file
        """
        self.outputFile.write(self.text)
        self.outputFile.write("\n\n")
        self.outputFile.write(tempAllData)
