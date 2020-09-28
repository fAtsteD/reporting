#!/usr/bin/python3
"""
Begining point of program
"""
import sys

import src.Transform


def main():
    """
    Main function for starting program
    """
    if len(sys.argv) >= 3:
        transform = src.Transform.Transform(sys.argv[1], sys.argv[2])
    if len(sys.argv) >= 2:
        transform = src.Transform.Transform(sys.argv[1])
    # TODO: Delete in release
    transform = src.Transform.Transform(os.path.realpath("tracking-hours.txt"))

    # Print transfered tasks
    print(transform.getReport())


if __name__ == "__main__":
    main()
