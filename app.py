#!/usr/bin/python3
"""
Begining point of program
"""
import os
import sys

from src.PrintConsole import PrintConsole
from src.PrintToFile import PrintToFile
from src.Transform import Transform


def main():
    """
    Main function for starting program
    """
    if len(sys.argv) >= 3:
        transform = Transform(sys.argv[1], sys.argv[2])
    if len(sys.argv) >= 2:
        transform = Transform(sys.argv[1])
    # TODO: Delete in release
    transform = Transform(os.path.realpath("tracking-hours.txt"))

    # Print transfered tasks
    printData = PrintToFile(transform)
    printData.print()


if __name__ == "__main__":
    main()
