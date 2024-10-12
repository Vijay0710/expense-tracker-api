"""Create Category Column for Transactions Table

Revision ID: 278138ccf08e
Revises: 8ffcab365c52
Create Date: 2024-10-11 21:30:20.128085

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import models


# revision identifiers, used by Alembic.
revision: str = '278138ccf08e'
down_revision: Union[str, None] = '8ffcab365c52'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        table_name='transactions',
        column=sa.Column(name="category", type_=sa.String(), default="Other")
    )


def downgrade() -> None:
    op.drop_column(
        table_name='transactions',
        column_name='category'
    )
