"""add monthly_usage and filejob.billed_at

Revision ID: c2d3e4f5a6b7
Revises: b1c2d3e4f5a6
Create Date: 2026-06-14 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "c2d3e4f5a6b7"
down_revision = "b1c2d3e4f5a6"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "monthly_usage",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("year_month", sa.Integer(), nullable=False),
        sa.Column("pages_used", sa.Integer(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id", "year_month", name="uq_monthly_usage_user_month"
        ),
    )
    op.create_index(
        op.f("ix_monthly_usage_user_id"), "monthly_usage", ["user_id"], unique=False
    )
    op.create_index(
        op.f("ix_monthly_usage_year_month"),
        "monthly_usage",
        ["year_month"],
        unique=False,
    )

    op.add_column(
        "file_jobs",
        sa.Column("billed_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade():
    op.drop_column("file_jobs", "billed_at")
    op.drop_index(op.f("ix_monthly_usage_year_month"), table_name="monthly_usage")
    op.drop_index(op.f("ix_monthly_usage_user_id"), table_name="monthly_usage")
    op.drop_table("monthly_usage")
