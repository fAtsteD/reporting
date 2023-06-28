import datetime
from typing import List

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Kind(Base):
    """
    It kind of tasks, because each kind can has short, full name etc.
    """
    __tablename__ = "kinds"

    id: Mapped[int] = mapped_column(primary_key=True)
    alias: Mapped[str] = mapped_column(unique=True)
    name: Mapped[str] = mapped_column()
    updated_at: Mapped[datetime.datetime] = mapped_column(
        default=sa.func.now(),
        server_default=sa.FetchedValue(),
        onupdate=sa.func.now(),
        server_onupdate=sa.FetchedValue()
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        default=sa.func.now(),
        server_default=sa.FetchedValue()
    )

    tasks: Mapped[List["Task"]] = relationship(back_populates="kind")

    def __str__(self):
        """
        One text line present of kind
        """
        return f"{self.alias} - {self.name}"
