from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.orm import Session

from reporting.database.models import Kind


def list_kinds(session: Session) -> Sequence[Kind]:
    return session.scalars(sa.select(Kind).order_by(Kind.name)).all()


def save_kind(session: Session, alias: str, name: str) -> Sequence[Kind]:
    kind = session.scalars(sa.select(Kind).where(Kind.alias == alias)).first()

    if kind:
        kind.name = name
    else:
        session.add(Kind(alias=alias, name=name))

    session.flush()

    return list_kinds(session)
