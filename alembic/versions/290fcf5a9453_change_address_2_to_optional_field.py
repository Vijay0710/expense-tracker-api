"""Change address 2 to Optional Field

Revision ID: 290fcf5a9453
Revises: c110b9256071
Create Date: 2024-09-22 22:41:11.930085

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '290fcf5a9453'
down_revision: Union[str, None] = 'c110b9256071'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        table_name='address',
        column_name='address_2',
        nullable=True
    )


def downgrade() -> None:
    op.alter_column(
        table_name='address',
        column_name='address_2',
        nullable=False
    )
