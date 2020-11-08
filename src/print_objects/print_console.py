#!/usr/bin/python3
"""
File with class for print report
"""
from src.print_objects.print_abstract import PrintAbstract
from src.transform.transform import Transform


class PrintConsole(PrintAbstract):
    """
    Print result to console
    """

    def print(self, transform: Transform):
        """
        Print to console
        """
        if (self._config.console_type_print == 1):
            self._parse_for_plain_print_1(transform)
        if (self._config.console_type_print == 2):
            self._parse_for_plain_print_2(transform)
        print(self.text)


if __name__ == "__main__":
    print("Run main app.py file")
