import datetime


class JiraConfig:
    """
    Config data related to the jira
    """
    is_use = False
    report_date: str | datetime.date = "last"

    # Urls
    server = ""

    # Auth
    login = ""
    password = ""

    # Tasks
    issue_key_base: list[str] = []

    def set_data(self, data: dict):
        """
        Set data to the class from data dict (file config usually)
        """
        if set(["server", "login", "password"]).issubset(data):
            self.server = data["server"].strip("/") + "/"
            self.login = data["login"]
            self.password = data["password"]
            self.is_use = True

        if "issue-key-base" in data:
            self.issue_key_base = data["issue-key-base"]
