"""
Object for holding report
"""


class Report:
    """
    Hold report from request get report
    Has additional methods

    timeRecords is not setted when create report

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
        "sent": str,
        "created": str,
        "updated": str,
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

    def next_task_order_num(self) -> int:
        """
        Next task for report from order number
        """
        if self.next_order_num == 0:
            if "timeRecords" in self.report and len(self.report["timeRecords"]) > 0:
                max_num = 1
                for record in self.report["timeRecords"]:
                    if record["orderNumber"] > max_num:
                        max_num = record["orderNumber"]

                self.next_order_num = max_num

        self.next_order_num += 1

        return self.next_order_num