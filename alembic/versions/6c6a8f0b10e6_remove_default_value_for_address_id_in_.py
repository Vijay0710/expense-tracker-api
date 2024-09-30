"""remove default value for address_id in users table

Revision ID: 6c6a8f0b10e6
Revises: 290fcf5a9453
Create Date: 2024-09-30 21:56:44.963524

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import uuid


# revision identifiers, used by Alembic.
revision: str = '6c6a8f0b10e6'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        table_name='users',
        column_name='address_id', 
        server_default=None,
        nullable=True
    )


def downgrade() -> None:
    op.alter_column(
        table_name='users',
        column_name='address_id', 
        server_default=uuid.uuid4(),
        nullable=False
    )
