"""Add OpenAI fields to chat_logs

Revision ID: dc5865e2f035
Revises: da71241c8300
Create Date: 2025-08-05 18:24:37.018303

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dc5865e2f035'
down_revision: Union[str, None] = 'da71241c8300'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new columns to chat_logs table
    op.add_column('chat_logs', sa.Column('user_id', sa.String(255), nullable=True))
    op.add_column('chat_logs', sa.Column('model_used', sa.String(100), nullable=True))
    op.add_column('chat_logs', sa.Column('confidence', sa.String(10), nullable=True))
    
    # Create indexes for better query performance
    op.create_index('ix_chat_logs_user_id', 'chat_logs', ['user_id'])
    op.create_index('ix_chat_logs_document_id', 'chat_logs', ['document_id'])


def downgrade() -> None:
    # Remove indexes
    op.drop_index('ix_chat_logs_document_id', 'chat_logs')
    op.drop_index('ix_chat_logs_user_id', 'chat_logs')
    
    # Remove columns
    op.drop_column('chat_logs', 'confidence')
    op.drop_column('chat_logs', 'model_used')
    op.drop_column('chat_logs', 'user_id')