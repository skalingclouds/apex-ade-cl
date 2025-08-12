"""add parsed_fields to documents

Revision ID: acb471839140
Revises: add_saved_schemas
Create Date: 2025-08-12 13:12:47.915489

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'acb471839140'
down_revision: Union[str, None] = 'add_saved_schemas'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Focused migration for SQLite: only add the new column
    op.add_column('documents', sa.Column('parsed_fields', sa.Text(), nullable=True))


def downgrade() -> None:
    # Only drop the added column
    op.drop_column('documents', 'parsed_fields')