import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from reporting import config_app
from reporting.models import Base


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    logged_seconds: Mapped[int] = mapped_column(default=0)
    summary: Mapped[str] = mapped_column(default="")

    kinds_id: Mapped[int] = mapped_column(sa.ForeignKey("kinds.id"))
    kind: Mapped["Kind"] = relationship(back_populates="tasks")

    projects_id: Mapped[int] = mapped_column(sa.ForeignKey("projects.id"))
    project: Mapped["Project"] = relationship(back_populates="tasks")

    updated_at: Mapped[datetime.datetime] = mapped_column(
        default=sa.func.now(),
        server_default=sa.FetchedValue(),
        onupdate=sa.func.now(),
        server_onupdate=sa.FetchedValue(),
    )
    created_at: Mapped[datetime.datetime] = mapped_column(default=sa.func.now(), server_default=sa.FetchedValue())

    reports_id: Mapped[int] = mapped_column(sa.ForeignKey("reports.id"))
    report: Mapped["Report"] = relationship(back_populates="tasks")

    @property
    def logged_rounded(self) -> int:
        """
        Round logged time to the config define minutes.

        If logged time has but after round it is 0, it sets round value for seconds
        """
        if self.logged_seconds <= 0:
            return 0

        config = config_app.config
        hours = self.logged_seconds / 60 // 60
        minutes = self.logged_seconds / 60 % 60

        if config.minute_round_to <= 0:
            return self.logged_seconds

        frac = minutes % config.minute_round_to

        if frac >= int(config.minute_round_to / 2) + 1:
            minutes = (minutes // config.minute_round_to + 1) * config.minute_round_to

            if minutes == 100:
                hours += 1
                minutes = 0
        else:
            minutes = minutes // config.minute_round_to * config.minute_round_to

        seconds: int = int(hours * 60 * 60 + minutes * 60)
        return seconds if seconds > 0 else config.minute_round_to * 60

    def logged_timedelta(self, logged_time: datetime.timedelta):
        """
        Add timedelta to the set logged seconds, it does not override
        value

        Firstly timedelta transforms to the seconds.
        """
        self.logged_seconds = (self.logged_seconds or 0) + int(round(logged_time.total_seconds(), 0))

    def __str__(self):
        """
        One text line present of task
        """
        logged_rounded = self.logged_rounded
        logged_hours = round(logged_rounded / 60 // 60)
        logged_hours_str = f"0{logged_hours}" if logged_hours < 10 else f"{logged_hours}"
        logged_minutes = round(logged_rounded / 60 % 60)
        logged_minutes_str = f"0{logged_minutes}" if logged_minutes < 10 else f"{logged_minutes}"

        return f"{logged_hours_str}:{logged_minutes_str} - {self.summary} - {self.project.name}"
