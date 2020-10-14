#!/usr/bin/python3
"""
Begining point of program
"""
import os
import sys

from src.config.config import Config
from src.transform.transform import Transform


def main():
    """
    Main function for starting program
    """
    config = Config()

    transform = Transform(config)

    # Pring data
    for print_object in config.outputs_day_report:
        print_object.print(transform)


if __name__ == "__main__":
    main()
