class ReportingConfig:
    """
    Config data related to the reporting
    """
    can_use = False

    # Urls
    url = ""
    suburl_auth = ""
    suburl_categories = ""
    suburl_projects = ""
    suburl_init = ""
    suburl_get_report = ""
    suburl_add_task = ""

    # Auth
    login = ""
    password = ""

    def set_data(self, data: dict):
        """
        Set data to the class from data dict (file config usually)
        """
        if set(["api-url", "suburl-auth", "login", "password"]).issubset(data):
            self.url = data["api-url"].strip("/") + "/"
            self.suburl_auth = data["suburl-auth"].strip("/") + "/"
            self.login = data["login"]
            self.password = data["password"]
            self.can_use = True

        if "suburl-categories" in data:
            self.suburl_categories = data["suburl-categories"].strip("/") + "/"

        if "suburl-projects" in data:
            self.suburl_projects = data["suburl-projects"].strip("/") + "/"

        if "suburl-init" in data:
            self.suburl_init = data["suburl-init"].strip("/") + "/"

        if "suburl-get-report" in data:
            self.suburl_get_report = data["suburl-get-report"].strip("/") + "/"

        if "suburl-add-task" in data:
            self.suburl_add_task = data["suburl-add-task"].strip("/") + "/"
