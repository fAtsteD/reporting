import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from config_app import config

from .base import Base


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    logged_seconds: Mapped[int] = mapped_column(
        default=0, server_default=sa.FetchedValue())
    summary: Mapped[str] = mapped_column(
        default="", server_default=sa.FetchedValue())
    kind: Mapped[str] = mapped_column(
        default=config.default_kind, server_default=sa.FetchedValue())
    project: Mapped[str] = mapped_column(
        default=config.default_project, server_default=sa.FetchedValue())
    updated_at: Mapped[datetime.datetime] = mapped_column(
        default=sa.func.now(), server_default=sa.FetchedValue(), onupdate=sa.func.now(), server_onupdate=sa.FetchedValue())
    created_at: Mapped[datetime.datetime] = mapped_column(
        default=sa.func.now(), server_default=sa.FetchedValue())

    reports_id: Mapped[int] = mapped_column(sa.ForeignKey("reports.id"))
    report: Mapped["Report"] = relationship(back_populates="tasks")

    def logged_rounded(self) -> int:
        """
        Round logged time to the config define minutes.

        If logged time has but after round it is 0, it sets round value for seconds
        """
        if self.logged_seconds <= 0:
            return 0.0

        hours = self.logged_seconds / 60 // 60
        minutes = self.logged_seconds / 60 % 60
        frac = minutes % config.minute_round_to

        if frac >= int(config.minute_round_to / 2) + 1:
            minutes = (minutes // config.minute_round_to + 1) * \
                config.minute_round_to

            if minutes == 60:
                hours += 1
                minutes = 0
        else:
            minutes = minutes // config.minute_round_to * config.minute_round_to

        rounded = datetime.timedelta(
            hours=hours, minutes=minutes).total_seconds()

        if rounded > 0:
            return rounded

        return datetime.timedelta(minutes=config.minute_round_to).total_seconds()

    def logged_timedelta(self, logged_time: datetime.timedelta):
        """
        Add timedelta to the setted logged seconds, it does not override
        value

        Firstly timedelta transforms to the seconds.
        """
        if self.logged_seconds is None:
            self.logged_seconds = 0

        self.logged_seconds += int(round(logged_time.total_seconds(), 0))

    def __str__(self):
        """
        One text line present of task
        """
        text = ""

        logged_hours = round(self.logged_seconds / 60 // 60)
        logged_hours_str = f"0{logged_hours}" if logged_hours < 10 else f"{logged_hours}"
        logged_minutes = round(self.logged_seconds / 60 % 60)
        logged_minutes_str = f"0{logged_minutes}" if logged_minutes < 10 else f"{logged_minutes}"
        text += f"{logged_hours_str}:{logged_minutes_str} - {self.summary} - {self.project}"

        return text
