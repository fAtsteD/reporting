import datetime


class ReportingConfig:
    """
    Config data related to the reporting
    """

    is_use = False
    report_date: str | datetime.date = "last"

    kinds = {}  # Kinds relation: key - from db, value - from reporting
    projects = {}  # Projects relation: key - from db, value - from reporting

    # Urls
    url = ""
    suburl_auth = ""
    suburl_logout = ""
    suburl_categories = ""
    suburl_categories_binding = ""
    suburl_projects = ""
    suburl_init = ""
    suburl_get_report = ""
    suburl_add_task = ""
    suburl_positions = ""

    # Auth
    login = ""
    password = ""

    def set_data(self, data: dict):
        """
        Set data to the class from data dict (file config usually)
        """
        if {"api-url", "suburl-auth", "login", "password"}.issubset(data):
            self.url = data["api-url"].strip("/") + "/"
            self.suburl_auth = data["suburl-auth"].strip("/") + "/"
            self.login = data["login"]
            self.password = data["password"]
            self.is_use = True

        if "suburl-categories" in data:
            self.suburl_categories = data["suburl-categories"].strip("/") + "/"

        if "suburl-categories-binding" in data:
            self.suburl_categories_binding = data["suburl-categories-binding"].strip("/") + "/"

        if "suburl-projects" in data:
            self.suburl_projects = data["suburl-projects"].strip("/") + "/"

        if "suburl-positions" in data:
            self.suburl_positions = data["suburl-positions"].strip("/") + "/"

        if "suburl-init" in data:
            self.suburl_init = data["suburl-init"].strip("/") + "/"

        if "suburl-get-report" in data:
            self.suburl_get_report = data["suburl-get-report"].strip("/") + "/"

        if "suburl-add-task" in data:
            self.suburl_add_task = data["suburl-add-task"].strip("/") + "/"

        if "suburl-logout" in data:
            self.suburl_logout = data["suburl-logout"].strip("/") + "/"

        if "kinds" in data:
            self.kinds = data["kinds"]

        if "projects" in data:
            self.projects = data["projects"]
