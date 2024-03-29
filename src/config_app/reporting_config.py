import datetime


class ReportingConfig:
    """
    Config data related to the reporting
    """

    is_use = False
    report_date: str | datetime.date = "last"
    safe_send_report_days: int = 0

    kinds = {}  # Kinds relation: key - from db, value - from reporting
    projects = {}  # Projects relation: key - from db, value - from reporting
    project_to_corp_struct_item = {}  # Projects relation: key - from db, value - from reporting corp struct item alias

    # Urls
    url = ""
    suburl_add_task = ""
    suburl_categories = ""
    suburl_categories_binding = ""
    suburl_corp_struct_items = ""
    suburl_get_report = ""
    suburl_init = ""
    suburl_login = ""
    suburl_logout = ""
    suburl_positions = ""
    suburl_projects = ""

    # Auth
    login = ""
    password = ""

    def set_data(self, data: dict):
        """
        Set data to the class from data dict (file config usually)
        """
        if {"api-url", "suburl-login", "login", "password"}.issubset(data):
            self.url = data["api-url"].strip("/") + "/"
            self.suburl_login = data["suburl-login"].strip("/") + "/"
            self.login = data["login"]
            self.password = data["password"]
            self.is_use = True

        if "kinds" in data:
            self.kinds = data["kinds"]

        if "projects" in data:
            self.projects = data["projects"]

        if "project-to-corp-struct-item" in data:
            self.project_to_corp_struct_item = data["project-to-corp-struct-item"]

        if "safe-send-report-days" in data and data["safe-send-report-days"] > 0:
            self.safe_send_report_days = data["safe-send-report-days"]

        if "suburl-add-task" in data:
            self.suburl_add_task = data["suburl-add-task"].strip("/") + "/"

        if "suburl-categories" in data:
            self.suburl_categories = data["suburl-categories"].strip("/") + "/"

        if "suburl-categories-binding" in data:
            self.suburl_categories_binding = data["suburl-categories-binding"].strip("/") + "/"

        if "suburl-corp-struct-items" in data:
            self.suburl_corp_struct_items = data["suburl-corp-struct-items"].strip("/") + "/"

        if "suburl-get-report" in data:
            self.suburl_get_report = data["suburl-get-report"].strip("/") + "/"

        if "suburl-init" in data:
            self.suburl_init = data["suburl-init"].strip("/") + "/"

        if "suburl-logout" in data:
            self.suburl_logout = data["suburl-logout"].strip("/") + "/"

        if "suburl-positions" in data:
            self.suburl_positions = data["suburl-positions"].strip("/") + "/"

        if "suburl-projects" in data:
            self.suburl_projects = data["suburl-projects"].strip("/") + "/"
