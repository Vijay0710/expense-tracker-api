"""change account balance to type double

Revision ID: 39ce2e906de3
Revises: 0dd7feead173
Create Date: 2024-11-24 17:13:53.129795

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '39ce2e906de3'
down_revision: Union[str, None] = '0dd7feead173'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        table_name='accounts',
        column_name='account_balance',
        postgresql_using = 'account_balance::DOUBLE PRECISION',
        existing_type=sa.BigInteger(),
        type_=sa.Double(),
    )


def downgrade() -> None:
    op.alter_column(
        table_name='accounts',
        column_name='account_balance',
        type_=sa.BigInteger()
    )
