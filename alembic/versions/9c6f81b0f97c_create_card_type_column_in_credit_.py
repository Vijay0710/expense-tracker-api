"""create card type column in Credit Account

Revision ID: 9c6f81b0f97c
Revises: 92557465c7c2
Create Date: 2024-12-20 21:15:31.031396

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9c6f81b0f97c'
down_revision: Union[str, None] = '92557465c7c2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        table_name='credit_account',
        column=sa.Column(
            name='card_type',
            type_=sa.String(),
            nullable=False,
            server_default='MASTERCARD'
        )
    )


def downgrade() -> None:
    op.drop_column(
        table_name='credit_account',
        column_name='card_type'
    )
