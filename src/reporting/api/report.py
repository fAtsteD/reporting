"""
Object for holding report
"""


class Report:
    """
    Hold report from request get report
    Has additional methods

    Report:
    {
        "id": int,
        "employeeId": int,
        "date": str,
        "timeRecords": [
            {
                "id": int,
                "hours": int,
                "invoiceHours": int,
                "salaryCoefficient": int,
                "departmentId": int,
                "categoryId": int,
                "projectId": int,
                "clientId": int,
                "description": str,
                "orderNumber": int,
                "salaryCoefficientType": int,
                "paidEvent": null,
                "pjmHours": null,
                "pjmApproved": bool,
                "pomApproved": bool,
                "overrideEmployeeId": null,
                "reportId": int,
                "eventId": null
            },
        ],
        "problems": str,
        "noTasks": bool,
        "sent": "2021-05-14T18:13:19.356+03:00",
        "created": str",
        "updated": str",
        "haveProblems": bool,
        "sentEmails": str,
        "cc": null
    }
    """

    def __init__(self, report: dict) -> None:
        """
        Initialize by report
        """
        self.report = report

        self.next_order_num = 0

    def next_task_order_num(self, num_report=0) -> int:
        """
        Next task for report from order number
        """
        if len(self.report[num_report]["timeRecords"]) == 0:
            self.next_order_num = 1
            return 1

        if self.next_order_num == 0:
            max_num = 1
            for record in self.report[num_report]["timeRecords"]:
                if record["orderNumber"] > max_num:
                    max_num = record["orderNumber"]

            self.next_order_num = max_num

        self.next_order_num += 1

        return self.next_order_num
