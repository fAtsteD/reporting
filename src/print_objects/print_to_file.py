#!/usr/bin/python3
"""
File with class for print report
"""
from src.print_objects.print_abstract import PrintAbstract
from src.transform.transform import Transform


class PrintToFile(PrintAbstract):
    """
    Print result report to file, default name of file "report.txt"

    Variables:
    - output_file - file for printing result
    """

    def __init__(self, output_file):
        self.output_file = open(output_file, "r+", encoding="utf-8")

    def print(self, transform: Transform):
        """
        Print to file
        """
        self._parse_for_plain_print(transform)
        temp = self.output_file.readlines()
        self.output_file.seek(0)
        self.output_file.write(self.text)
        self.output_file.write("\n\n")
        self.output_file.writelines(temp)


if __name__ == "__main__":
    print("Run main app.py file")
