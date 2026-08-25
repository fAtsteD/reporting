import datetime

import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.orm import Session

from reporting.database.models import Report, Task


def find_by_date(session: Session, report_date: datetime.date) -> Report | None:
    return session.scalars(_select_report().where(Report.date == report_date)).first()


def find_by_date_or_last(session: Session, report_date: datetime.date | None) -> Report | None:
    if report_date is None:
        return find_last(session)

    return find_by_date(session, report_date)


def find_by_id(session: Session, report_id: int) -> Report | None:
    return session.scalars(_select_report().where(Report.id == report_id)).first()


def find_last(session: Session) -> Report | None:
    return session.scalars(_select_report().order_by(Report.date.desc())).first()


def _select_report() -> sa.Select[tuple[Report]]:
    return sa.select(Report).options(
        orm.selectinload(Report.tasks).selectinload(Task.kind),
        orm.selectinload(Report.tasks).selectinload(Task.project),
    )
