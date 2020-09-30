#!/usr/bin/python3
"""
Begining point of program
"""
import os
import sys

from src.PrintConsole import PrintConsole
from src.PrintToFile import PrintToFile
from src.Transform import Transform
from src.Window import Window


def main():
    """
    Main function for starting program
    """
    if len(sys.argv) >= 3:
        transform = Transform(os.path.realpath(
            sys.argv[1]))
        printData = PrintToFile(transform, os.path.realpath(
            sys.argv[2]))
    if len(sys.argv) >= 2:
        transform = Transform(os.path.realpath(sys.argv[1]))
        printData = PrintConsole()
    if len(sys.argv) < 2:
        transform = Transform(os.path.realpath("tracking-hours.txt"))
        printData = PrintConsole()

    printData.print()


if __name__ == "__main__":
    main()
