"""Add archive fields to documents table

Revision ID: add_archive_fields
Revises: 162a0e3a6453
Create Date: 2025-08-06

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text

# revision identifiers
revision = 'add_archive_fields'
down_revision = '162a0e3a6453'
branch_labels = None
depends_on = None


def upgrade():
    # Add archive fields to documents table
    op.add_column('documents', sa.Column('archived', sa.Boolean(), nullable=False, server_default='0'))
    op.add_column('documents', sa.Column('archived_at', sa.DateTime(), nullable=True))
    op.add_column('documents', sa.Column('archived_by', sa.String(255), nullable=True))
    
    # Create index for faster queries on archived status
    op.create_index('idx_documents_archived', 'documents', ['archived'])
    op.create_index('idx_documents_status_archived', 'documents', ['status', 'archived'])


def downgrade():
    # Drop indexes
    op.drop_index('idx_documents_status_archived', 'documents')
    op.drop_index('idx_documents_archived', 'documents')
    
    # Remove columns
    op.drop_column('documents', 'archived_by')
    op.drop_column('documents', 'archived_at')
    op.drop_column('documents', 'archived')