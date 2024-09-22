import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

import config_app
from models import Base
from models.task import Task


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

    def total_seconds(self) -> int:
        """
        Total seconds of the report's all tasks
        """
        sum_seconds = 0

        for task in self.tasks:
            sum_seconds += task.logged_seconds if task.logged_seconds is not None and task.logged_seconds > 0 else 0

        return sum_seconds

    def remove_tasks(self):
        """
        Remove tasks in the report
        """
        config = config_app.config

        for task in self.tasks:
            self.updated_at = sa.func.now()
            config.sqlite_session.delete(task)

        config.sqlite_session.commit()

    def __str__(self):
        """
        Report to the text present, it is multiline
        """
        config = config_app.config
        text = self.date.strftime("%d.%m.%Y") + " (" + datetime.date.today().strftime("%d.%m.%Y") + ")\n"

        total_hours = round(self.total_seconds() / 60 // 60)
        total_hours_str = f"0{total_hours}" if total_hours < 10 else f"{total_hours}"
        total_minutes = round(self.total_seconds() / 60 % 60)
        total_minutes_str = f"0{total_minutes}" if total_minutes < 10 else f"{total_minutes}"
        text += f"Summary time: {total_hours_str}:{total_minutes_str}\n"

        indent = "  "
        tasks = (
            config.sqlite_session.query(Task)
            .filter(Task.report.has(Report.id == self.id))
            .order_by(Task.kinds_id)
            .all()
        )
        text += "Tasks:\n"
        task_indent = indent + indent
        previous_kind = ""

        for task in tasks:
            if task.kind.name != previous_kind:
                text += indent + task.kind.name + ":\n"

            text += f"{task_indent}{task}\n"
            previous_kind = task.kind.name

        return text
