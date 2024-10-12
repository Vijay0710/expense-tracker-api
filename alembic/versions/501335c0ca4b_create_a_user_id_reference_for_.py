"""Create a user id reference for transactions

Revision ID: 501335c0ca4b
Revises: 6c6a8f0b10e6
Create Date: 2024-10-06 21:33:38.450920

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '501335c0ca4b'
down_revision: Union[str, None] = '6c6a8f0b10e6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(table_name='transactions', column=sa.Column('user_id', sa.UUID(as_uuid=True), nullable=False))
    op.create_foreign_key(
        'fk_user_transaction',
        'transactions',
        'users',
        ['user_id'],
        ['id']
    )


def downgrade() -> None:
    op.drop_column(table_name='transactions',column_name='user_id')
    op.drop_constraint(
        'fk_user_transaction',
        'transactions',
        type_='foreignkey'
    )
