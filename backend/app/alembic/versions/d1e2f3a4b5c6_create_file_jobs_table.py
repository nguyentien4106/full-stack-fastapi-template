"""create_file_jobs_table

Revision ID: d1e2f3a4b5c6
Revises: a24416477b07
Create Date: 2026-04-25 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = 'd1e2f3a4b5c6'
down_revision = 'a24416477b07'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'file_jobs',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('job_id', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column('file_id', sa.Uuid(), nullable=False),
        sa.Column('state', sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False),
        sa.Column('total_pages', sa.Integer(), nullable=True),
        sa.Column('extracted_pages', sa.Integer(), nullable=True),
        sa.Column('start_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('end_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('json_url', sqlmodel.sql.sqltypes.AutoString(length=4000), nullable=True),
        sa.Column('markdown_url', sqlmodel.sql.sqltypes.AutoString(length=4000), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['file_id'], ['files.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_file_jobs_job_id'), 'file_jobs', ['job_id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_file_jobs_job_id'), table_name='file_jobs')
    op.drop_table('file_jobs')
