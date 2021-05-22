#!/usr/bin/python3
"""
File with class for print report
"""
from ..config_app import config
from ..transform import DayData, Task


class PrintAbstract():
    """
    Abstract for printing
    """

    def print(self, day_data: DayData):
        """
        Override in inherited classes for printing
        """
        print("Use another any inherited object for printing")

    def _parse_for_plain_print_1(self, day_data: DayData) -> str:
        """
        Parse data for printing type 1
        """
        day_time = 0.0
        indent = config.text_indent
        text = day_data.date.strftime("%d.%m.%Y") + "\n"

        text_tasks = ""
        for kind in day_data.kinds:
            text_tasks += indent + kind + ":\n"

            task_indent = indent + indent
            for task in day_data.get_tasks_by_kind(kind):
                text_tasks += task_indent + task.get_string_time() + "h - " + \
                    task.name + "\n"
                day_time += float(task.get_string_time())

        text += "Summary time: " + str(day_time) + "h\n"
        text += "Tasks:\n"
        text += text_tasks
        return text
