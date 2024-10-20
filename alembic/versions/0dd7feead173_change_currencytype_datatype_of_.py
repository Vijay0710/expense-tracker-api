"""Change CurrencyType datatype of Transactions

Revision ID: 0dd7feead173
Revises: b92e96dc39b4
Create Date: 2024-10-12 23:53:27.030325

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import models


# revision identifiers, used by Alembic.
revision: str = '0dd7feead173'
down_revision: Union[str, None] = 'b92e96dc39b4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        table_name='transactions',
        column_name='transaction_currency_type',
        nullable=False,
        postgresql_using='transaction_currency_type::text::CurrencyType',
        type_=sa.Enum(models.CurrencyType)
    )


def downgrade() -> None:
    op.alter_column(
        table_name='transactions',
        column_name='transaction_currency_type',
        type_=sa.String(),
        nullable=True,
    )
