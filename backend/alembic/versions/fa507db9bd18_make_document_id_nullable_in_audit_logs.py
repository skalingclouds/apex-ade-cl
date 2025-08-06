"""Make document_id nullable in audit_logs

Revision ID: fa507db9bd18
Revises: dc5865e2f035
Create Date: 2025-08-05 20:10:03.089730

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fa507db9bd18'
down_revision: Union[str, None] = 'dc5865e2f035'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Make document_id nullable in audit_logs table
    with op.batch_alter_table('audit_logs') as batch_op:
        batch_op.alter_column('document_id',
                              existing_type=sa.INTEGER(),
                              nullable=True)


def downgrade() -> None:
    # Make document_id not nullable again
    with op.batch_alter_table('audit_logs') as batch_op:
        batch_op.alter_column('document_id',
                              existing_type=sa.INTEGER(),
                              nullable=False)