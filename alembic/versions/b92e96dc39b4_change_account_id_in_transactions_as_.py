"""Change account id in Transactions as Foregin Key ref to Accounts

Revision ID: b92e96dc39b4
Revises: d7dfe00c7ee9
Create Date: 2024-10-12 23:17:34.099325

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b92e96dc39b4'
down_revision: Union[str, None] = 'd7dfe00c7ee9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_foreign_key(
        'transactions_account_fk',
        'transactions',
        'accounts',
        ['account_id'],  
        ['id'],
    )


def downgrade() -> None:
    op.drop_constraint(
        table_name='transactions',
        constraint_name='transactions_account_fk'
    )
