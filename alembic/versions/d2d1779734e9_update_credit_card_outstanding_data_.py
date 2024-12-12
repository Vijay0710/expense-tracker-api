"""Update credit card outstanding data type to double

Revision ID: d2d1779734e9
Revises: a124603073ca
Create Date: 2024-12-12 16:46:56.893774

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd2d1779734e9'
down_revision: Union[str, None] = 'a124603073ca'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        table_name='credit_account',
        column_name='credit_card_outstanding',
        postgresql_using = 'credit_card_outstanding::DOUBLE PRECISION',
        type_=sa.Double(),
        existing_type=sa.BigInteger()
    )


def downgrade() -> None:
        op.alter_column(
        table_name='credit_account',
        column_name='credit_card_outstanding',
        type_=sa.BigInteger(),
        existing_type=sa.Double()
    )
