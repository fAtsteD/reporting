"""
For config param dictionary object
"""


class Dictionary:
    """
    Save all dictionary. Transform data
    """
    tasks = {}
    kinds = {}
    projects = {}

    def set_data(self, data: dict):
        """
        Set data to the object
        """
        if "task" in data:
            self.tasks = data["task"]
        if "type" in data:
            self.kinds = data["type"]
        if "project" in data:
            self.projects = data["project"]

    def translate_task(self, text: str) -> str:
        """
        Translate task if it sets
        Return translated or original
        """
        if len(self.tasks) < 1:
            return text

        if text in self.tasks:
            return self.tasks[text]

        return text

    def translate_kind(self, text: str) -> str:
        """
        Translate kind if it sets
        Return translated or original
        """
        if len(self.kinds) < 1:
            return text

        if text in self.kinds:
            return self.kinds[text]

        return text

    def translate_project(self, text: str) -> str:
        """
        Translate project if it sets
        Return translated or original
        """
        if len(self.projects) < 1:
            return text

        if text in self.projects:
            return self.projects[text]

        return text
