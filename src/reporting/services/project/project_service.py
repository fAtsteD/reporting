from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.orm import Session

from reporting.database.models import Project


def list_projects(session: Session) -> Sequence[Project]:
    return session.scalars(sa.select(Project).order_by(Project.name)).all()


def save_project(session: Session, alias: str, name: str) -> Sequence[Project]:
    project = session.scalars(sa.select(Project).where(Project.alias == alias)).first()

    if project:
        project.name = name
    else:
        session.add(Project(alias=alias, name=name))

    session.flush()

    return list_projects(session)
