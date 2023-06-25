from datetime import datetime


class TaskLine:
    """
    Simple dto for structure parsed line of task
    """

    def __init__(self):
        self.time_begin: datetime = None
        self.summary = ""
        self.kind = ""
        self.project = ""