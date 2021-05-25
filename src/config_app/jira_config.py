class JiraConfig:
    """
    Config data related to the jira
    """
    can_use = False

    # Urls
    server = ""

    # Auth
    login = ""
    password = ""

    # Tasks
    issue_key_base = ""

    def set_data(self, data: dict):
        """
        Set data to the class from data dict (file config usually)
        """
        if set(["server", "login", "password"]).issubset(data):
            self.server = data["server"].strip("/") + "/"
            self.login = data["login"]
            self.password = data["password"]
            self.can_use = True

        if "issue-key-base" in data:
            self.issue_key_base = data["issue-key-base"]
