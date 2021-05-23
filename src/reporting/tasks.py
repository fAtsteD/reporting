"""
Work with tasks from app
"""
from transform import DayData

from .api import *
from .common import get_api


def send_tasks(day_data: DayData) -> None:
    """
    Send task to the report. Print status each
    """
    api = get_api()

    report = api.get_report(day_data.date)

    print("\nSend task:")
    for task in day_data.tasks:
        api.add_task(task, report)
        print("[+] " + task.name)
