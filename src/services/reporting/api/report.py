class Report:
    """
    Hold report from request get report
    Has additional methods

    timeRecords is not set when create report

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
        self._report = report
        self._next_order_num = 0

    def get_id(self) -> int:
        """
        Server report id
        """
        return self._report["id"]

    def next_task_order_num(self) -> int:
        """
        Next task for report from order number
        """
        if self._next_order_num == 0:
            if "timeRecords" in self._report and len(self._report["timeRecords"]) > 0:
                max_num = 1
                for record in self._report["timeRecords"]:
                    if record["orderNumber"] > max_num:
                        max_num = record["orderNumber"]

                self._next_order_num = max_num

        self._next_order_num += 1

        return self._next_order_num
