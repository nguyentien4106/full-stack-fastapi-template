"""drop_job_fields_from_files_add_err_msg_to_file_jobs

Revision ID: e2f3a4b5c6d7
Revises: d1e2f3a4b5c6
Create Date: 2026-04-25 00:01:00.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = 'e2f3a4b5c6d7'
down_revision = 'd1e2f3a4b5c6'
branch_labels = None
depends_on = None


def upgrade():
    # Drop job-tracking columns from files table
    op.drop_index('ix_files_job_id', table_name='files')
    op.drop_column('files', 'job_id')
    op.drop_column('files', 'job_status')
    op.drop_column('files', 'err_msg')

    # Add err_msg to file_jobs table
    op.add_column(
        'file_jobs',
        sa.Column('err_msg', sqlmodel.sql.sqltypes.AutoString(length=500), nullable=True),
    )


def downgrade():
    # Restore columns on files table
    op.add_column('files', sa.Column('err_msg', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True))
    op.add_column('files', sa.Column('job_status', sqlmodel.sql.sqltypes.AutoString(length=50), nullable=True))
    op.add_column('files', sa.Column('job_id', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True))
    op.create_index('ix_files_job_id', 'files', ['job_id'], unique=False)

    # Drop err_msg from file_jobs
    op.drop_column('file_jobs', 'err_msg')
