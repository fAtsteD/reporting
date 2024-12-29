import datetime

import sqlalchemy as sa
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from reporting import config, database


class Base(DeclarativeBase):
    pass


class Kind(Base):
    """
    It kind of tasks, because each kind can has short, full name etc.
    """

    __tablename__ = "kinds"

    id: Mapped[int] = mapped_column(primary_key=True)
    alias: Mapped[str] = mapped_column(unique=True)
    name: Mapped[str]
    updated_at: Mapped[datetime.datetime] = mapped_column(
        default=sa.func.now(),
        server_default=sa.FetchedValue(),
        onupdate=sa.func.now(),
        server_onupdate=sa.FetchedValue(),
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        default=sa.func.now(),
        server_default=sa.FetchedValue(),
    )

    tasks: Mapped[list["Task"]] = relationship(back_populates="kind")

    def __str__(self):
        """
        One text line present of kind
        """
        return f"{self.alias} - {self.name}"


class Project(Base):
    """
    It's project of tasks, because each project can has short, name etc.
    """

    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    alias: Mapped[str] = mapped_column(unique=True)
    name: Mapped[str]
    updated_at: Mapped[datetime.datetime] = mapped_column(
        default=sa.func.now(),
        server_default=sa.FetchedValue(),
        onupdate=sa.func.now(),
        server_onupdate=sa.FetchedValue(),
    )
    created_at: Mapped[datetime.datetime] = mapped_column(default=sa.func.now(), server_default=sa.FetchedValue())

    tasks: Mapped[list["Task"]] = relationship(back_populates="project")

    def __str__(self):
        """
        One text line present of kind
        """
        return f"{self.alias} - {self.name}"


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[datetime.date] = mapped_column(index=True)
    updated_at: Mapped[datetime.datetime] = mapped_column(
        default=sa.func.now(),
        server_default=sa.FetchedValue(),
        onupdate=sa.func.now(),
        server_onupdate=sa.FetchedValue(),
    )
    created_at: Mapped[datetime.datetime] = mapped_column(default=sa.func.now(), server_default=sa.FetchedValue())

    tasks: Mapped[list["Task"]] = relationship(back_populates="report")

    @property
    def total_rounded_seconds(self) -> int:
        return sum(map(lambda task: task.logged_rounded, self.tasks))

    @property
    def total_seconds(self) -> int:
        return sum(map(lambda task: task.logged_seconds, self.tasks))

    def remove_tasks(self):
        """
        Remove tasks in the report
        """
        for task in self.tasks:
            self.updated_at = sa.func.now()
            database.session.delete(task)

        database.session.commit()

    def __str__(self):
        """
        Report to the text present, it is multiline
        """
        text = self.date.strftime("%d.%m.%Y") + " (" + datetime.date.today().strftime("%d.%m.%Y") + ")\n"

        total_seconds = self.total_rounded_seconds
        total_hours = round(total_seconds / 60 // 60)
        total_hours_str = f"0{total_hours}" if total_hours < 10 else f"{total_hours}"
        total_minutes = round(total_seconds / 60 % 60)
        total_minutes_str = f"0{total_minutes}" if total_minutes < 10 else f"{total_minutes}"
        text += f"Summary time: {total_hours_str}:{total_minutes_str}\n"

        indent = "  "
        tasks = (
            database.session.query(Task)
            .filter(Task.report.has(Report.id == self.id))
            .order_by(Task.kinds_id, Task.summary)
            .all()
        )

        if len(tasks) == 0:
            text += "Report does not have tasks\n"
            return text

        text += "Tasks:\n"
        task_indent = indent + indent
        previous_kind = ""

        for task in tasks:
            if task.kind.name != previous_kind:
                text += indent + task.kind.name + ":\n"

            text += f"{task_indent}{task}\n"
            previous_kind = task.kind.name

        return text


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
