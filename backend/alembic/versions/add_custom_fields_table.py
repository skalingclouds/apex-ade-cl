"""Add custom fields table

Revision ID: add_custom_fields
Revises: fa507db9bd18
Create Date: 2024-12-06 23:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_custom_fields'
down_revision = 'fa507db9bd18'
branch_labels = None
depends_on = None


def upgrade():
    # Create custom_fields table
    op.create_table('custom_fields',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('type', sa.String(length=50), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('usage_count', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_custom_fields_id'), 'custom_fields', ['id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_custom_fields_id'), table_name='custom_fields')
    op.drop_table('custom_fields')