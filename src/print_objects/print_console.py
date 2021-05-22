#!/usr/bin/python3
"""
File with class for print report
"""
from src.transform.transform import DayData

from ..config_app import config
from .print_abstract import PrintAbstract


class PrintConsole(PrintAbstract):
    """
    Print result to console
    """

    def print(self, day_data: DayData):
        """
        Print to console
        """
        if (config.console_type_print == 1):
            print(self._parse_for_plain_print_1(day_data))
