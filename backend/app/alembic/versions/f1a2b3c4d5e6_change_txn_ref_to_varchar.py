"""change txn_ref to varchar

Revision ID: f1a2b3c4d5e6
Revises: 16a9754259d0
Create Date: 2026-04-25 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = 'f1a2b3c4d5e6'
down_revision = '16a9754259d0'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        'topup_transactions',
        'txn_ref',
        existing_type=sa.Integer(),
        type_=sqlmodel.sql.sqltypes.AutoString(length=100),
        existing_nullable=True,
        postgresql_using="txn_ref::varchar(100)",
    )


def downgrade():
    op.alter_column(
        'topup_transactions',
        'txn_ref',
        existing_type=sqlmodel.sql.sqltypes.AutoString(length=100),
        type_=sa.Integer(),
        existing_nullable=True,
        postgresql_using="txn_ref::integer",
    )
