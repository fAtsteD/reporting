"""cascade delete tasks with report

Revision ID: 4ae94e30939b
Revises: bb4138ae3afb
Create Date: 2026-08-16 12:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "4ae94e30939b"
down_revision: str | None = "bb4138ae3afb"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_tasks_table = sa.Table(
    "tasks",
    sa.MetaData(),
    sa.Column("id", sa.Integer(), nullable=False),
    sa.Column("logged_seconds", sa.Integer(), nullable=False),
    sa.Column("summary", sa.String(), nullable=False),
    sa.Column("kinds_id", sa.Integer(), nullable=False),
    sa.Column("projects_id", sa.Integer(), nullable=False),
    sa.Column("updated_at", sa.DateTime(), server_default=sa.FetchedValue(), nullable=False),
    sa.Column("created_at", sa.DateTime(), server_default=sa.FetchedValue(), nullable=False),
    sa.Column("reports_id", sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(
        ["kinds_id"],
        ["kinds.id"],
    ),
    sa.ForeignKeyConstraint(
        ["projects_id"],
        ["projects.id"],
    ),
    sa.ForeignKeyConstraint(["reports_id"], ["reports.id"], ondelete="CASCADE"),
    sa.PrimaryKeyConstraint("id"),
)

_tasks_table_downgrade = sa.Table(
    "tasks",
    sa.MetaData(),
    sa.Column("id", sa.Integer(), nullable=False),
    sa.Column("logged_seconds", sa.Integer(), nullable=False),
    sa.Column("summary", sa.String(), nullable=False),
    sa.Column("kinds_id", sa.Integer(), nullable=False),
    sa.Column("projects_id", sa.Integer(), nullable=False),
    sa.Column("updated_at", sa.DateTime(), server_default=sa.FetchedValue(), nullable=False),
    sa.Column("created_at", sa.DateTime(), server_default=sa.FetchedValue(), nullable=False),
    sa.Column("reports_id", sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(
        ["kinds_id"],
        ["kinds.id"],
    ),
    sa.ForeignKeyConstraint(
        ["projects_id"],
        ["projects.id"],
    ),
    sa.ForeignKeyConstraint(
        ["reports_id"],
        ["reports.id"],
    ),
    sa.PrimaryKeyConstraint("id"),
)


def upgrade() -> None:
    with op.batch_alter_table("tasks", copy_from=_tasks_table) as batch_op:
        batch_op.create_foreign_key(
            "fk_tasks_reports_id_reports",
            "reports",
            ["reports_id"],
            ["id"],
            ondelete="CASCADE",
        )


def downgrade() -> None:
    with op.batch_alter_table("tasks", copy_from=_tasks_table_downgrade) as batch_op:
        batch_op.create_foreign_key(
            "fk_tasks_reports_id_reports",
            "reports",
            ["reports_id"],
            ["id"],
        )
