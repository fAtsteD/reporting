import datetime
import re

import sqlalchemy as sa
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.types import DateTime, TypeDecorator

from reporting import config

_SUMMARY_KEY_PATTERN = re.compile(r"^([^\s:]*[0-9][^\s:]*):\s*(.+)$")


class DBDatetimeType(TypeDecorator[datetime.datetime]):
    cache_ok = True
    impl = DateTime(timezone=True)

    def process_bind_param(self, value: datetime.datetime | None, dialect) -> datetime.datetime | None:
        if not value:
            return None

        if value.tzinfo is None:
            return value.replace(tzinfo=datetime.UTC)

        return value.astimezone(datetime.UTC)

    def process_result_value(self, value: datetime.datetime | None, dialect) -> datetime.datetime | None:
        if not value:
            return None

        return value.replace(tzinfo=datetime.UTC)


class Base(DeclarativeBase):
    pass


class Kind(Base):
    __tablename__ = "kinds"

    id: Mapped[int] = mapped_column(primary_key=True)
    alias: Mapped[str] = mapped_column(unique=True)
    name: Mapped[str]
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DBDatetimeType(),
        default=lambda: datetime.datetime.now(datetime.UTC),
        onupdate=lambda: datetime.datetime.now(datetime.UTC),
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DBDatetimeType(), default=lambda: datetime.datetime.now(datetime.UTC)
    )

    tasks: Mapped[list["Task"]] = relationship(back_populates="kind")


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    alias: Mapped[str] = mapped_column(unique=True)
    name: Mapped[str]
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DBDatetimeType(),
        default=lambda: datetime.datetime.now(datetime.UTC),
        onupdate=lambda: datetime.datetime.now(datetime.UTC),
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DBDatetimeType(), default=lambda: datetime.datetime.now(datetime.UTC)
    )

    tasks: Mapped[list["Task"]] = relationship(back_populates="project")


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[datetime.date] = mapped_column(index=True)
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DBDatetimeType(),
        default=lambda: datetime.datetime.now(datetime.UTC),
        onupdate=lambda: datetime.datetime.now(datetime.UTC),
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DBDatetimeType(), default=lambda: datetime.datetime.now(datetime.UTC)
    )

    tasks: Mapped[list["Task"]] = relationship(back_populates="report", cascade="all, delete-orphan")

    @property
    def total_rounded_seconds(self) -> int:
        return sum(task.logged_rounded for task in self.tasks)

    @property
    def total_seconds(self) -> int:
        return sum(task.logged_seconds for task in self.tasks)


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
        DBDatetimeType(),
        default=lambda: datetime.datetime.now(datetime.UTC),
        onupdate=lambda: datetime.datetime.now(datetime.UTC),
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DBDatetimeType(), default=lambda: datetime.datetime.now(datetime.UTC)
    )

    reports_id: Mapped[int] = mapped_column(sa.ForeignKey("reports.id", ondelete="CASCADE"))
    report: Mapped["Report"] = relationship(back_populates="tasks")

    @property
    def logged_rounded(self) -> int:
        """
        Round logged time to the config define minutes.

        If logged time has but after round it is 0, it sets round value for seconds
        """
        if self.logged_seconds <= 0:
            return 0

        hours = self.logged_seconds / 60 // 60
        minutes = self.logged_seconds / 60 % 60

        if config.app.minute_round_to <= 0:
            return self.logged_seconds

        frac = minutes % config.app.minute_round_to

        if frac >= int(config.app.minute_round_to / 2) + 1:
            minutes = (minutes // config.app.minute_round_to + 1) * config.app.minute_round_to

            if minutes == 100:
                hours += 1
                minutes = 0
        else:
            minutes = minutes // config.app.minute_round_to * config.app.minute_round_to

        seconds: int = int(hours * 60 * 60 + minutes * 60)
        return seconds if seconds > 0 else config.app.minute_round_to * 60

    @property
    def summary_key(self) -> str:
        matched_summary = _SUMMARY_KEY_PATTERN.match(self.summary)

        if matched_summary is None:
            return ""

        return matched_summary.group(1)

    @property
    def summary_text(self) -> str:
        matched_summary = _SUMMARY_KEY_PATTERN.match(self.summary)

        if matched_summary is None:
            return self.summary

        return matched_summary.group(2).strip()

    def logged_timedelta(self, logged_time: datetime.timedelta):
        """
        Add timedelta to the set logged seconds, it does not override
        value

        Firstly timedelta transforms to the seconds.
        """
        self.logged_seconds = (self.logged_seconds or 0) + int(round(logged_time.total_seconds(), 0))
