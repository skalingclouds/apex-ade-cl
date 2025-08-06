"""Merge migration heads

Revision ID: da71241c8300
Revises: 25fa189ce99a, add_archive_fields
Create Date: 2025-08-05 18:24:30.736079

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'da71241c8300'
down_revision: Union[str, None] = ('25fa189ce99a', 'add_archive_fields')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass