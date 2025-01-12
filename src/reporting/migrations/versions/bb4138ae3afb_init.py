"""init

Revision ID: bb4138ae3afb
Revises:
Create Date: 2025-01-11 19:51:04.113700

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "bb4138ae3afb"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "kinds",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("alias", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.FetchedValue(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.FetchedValue(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("alias"),
    )
    op.create_table(
        "projects",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("alias", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.FetchedValue(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.FetchedValue(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("alias"),
    )
    op.create_table(
        "reports",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.FetchedValue(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.FetchedValue(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_reports_date"), "reports", ["date"], unique=False)
    op.create_table(
        "tasks",
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


def downgrade() -> None:
    op.drop_table("tasks")
    op.drop_index(op.f("ix_reports_date"), table_name="reports")
    op.drop_table("reports")
    op.drop_table("projects")
    op.drop_table("kinds")
