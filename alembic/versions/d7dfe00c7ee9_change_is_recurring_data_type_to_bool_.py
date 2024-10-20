"""Change is_recurring data type to bool in Transactions

Revision ID: d7dfe00c7ee9
Revises: 278138ccf08e
Create Date: 2024-10-12 22:56:51.036936

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd7dfe00c7ee9'
down_revision: Union[str, None] = '278138ccf08e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        table_name='transactions',
        column_name='is_recurring',
        nullable=False,
        postgresql_using='is_recurring::boolean',
        type_= sa.Boolean(),
    )


def downgrade() -> None:
    op.alter_column(
        table_name='transactions',
        column_name='is_recurring',
        nullable=True,
        type_= sa.String()
    )
