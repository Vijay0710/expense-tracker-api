"""Change account number type to str

Revision ID: 92557465c7c2
Revises: d2d1779734e9
Create Date: 2024-12-20 15:33:12.381056

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '92557465c7c2'
down_revision: Union[str, None] = 'd2d1779734e9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        table_name='accounts',
        column_name='account_number',
        nullable=False,
        postgresql_using='account_number::bigint',
        type_=sa.String()
    )


def downgrade() -> None:
        op.alter_column(
        table_name='accounts',
        column_name='account_number',
        nullable=False,
        type_=sa.BigInteger()
    )
