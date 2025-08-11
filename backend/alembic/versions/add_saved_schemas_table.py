"""Add saved schemas table

Revision ID: add_saved_schemas
Revises: add_document_chunking
Create Date: 2025-08-11
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'add_saved_schemas'
down_revision = 'add_document_chunking'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'saved_schemas',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=150), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('fields_json', sa.Text(), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )


def downgrade():
    op.drop_table('saved_schemas')


