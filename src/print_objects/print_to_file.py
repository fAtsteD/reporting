#!/usr/bin/python3
"""
File with class for print report
"""
from src.transform.transform import DayData

from ..config_app import config
from .print_abstract import PrintAbstract


class PrintToFile(PrintAbstract):
    """
    Print result report to file, default name of file "report.txt"
    """

    def print(self, day_data: DayData):
        """
        Print to file
        """
        text = ""
        if (config.file_type_print == 1):
            text = self._parse_for_plain_print_1(day_data)

        with open(config.output_file_day, "r+", encoding="utf-8") as output_file:
            temp = output_file.readlines()
            output_file.seek(0)
            output_file.write(text)
            output_file.write("\n\n")
            output_file.writelines(temp)
