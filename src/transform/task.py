import datetime

from ..config_app import config


class Task:
    """
    Hold all data for one task
    """

    def __init__(self):
        self.time: datetime.timedelta = None
        self.time_begin: datetime.datetime = None
        self.name: str = ""
        self.project: str = config.default_project
        self.kind: str = config.default_kind

    def get_transformed_time(self) -> float:
        """
        Rounded time from 60 minutes to 100 and return like float value of hours
        """
        time = self.get_scaled_time()
        return time.seconds / 60 / 60

    def get_scaled_time(self) -> datetime.timedelta:
        """
        Return time with scaling to the config minutes round
        """
        if self.time is None:
            return datetime.timedelta(hours=0, minutes=0)

        hours = self.time.seconds / 60 // 60
        minutes = self.time.seconds / 60 % 60

        frac = minutes % config.minute_round_to
        if frac >= int(config.minute_round_to / 2) + 1:
            minutes = (minutes // config.minute_round_to + 1) * \
                config.minute_round_to
            if minutes == 100:
                hours += 1
                minutes = 0
        else:
            minutes = minutes // config.minute_round_to * config.minute_round_to

        return datetime.timedelta(hours=hours, minutes=minutes)
