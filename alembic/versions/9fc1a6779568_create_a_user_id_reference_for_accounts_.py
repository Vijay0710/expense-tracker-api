"""Create a user id reference for accounts table

Revision ID: 9fc1a6779568
Revises: 501335c0ca4b
Create Date: 2024-10-06 21:57:41.643283

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9fc1a6779568'
down_revision: Union[str, None] = '501335c0ca4b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(table_name='accounts', column=sa.Column('user_id', sa.UUID(as_uuid=True), nullable=False))
    op.create_foreign_key(
        'fk_user_accounts',
        'accounts',
        'users',
        ['user_id'],
        ['id']
    )


def downgrade() -> None:
    op.drop_column(table_name='users',column_name='user_id')
    op.drop_constraint(
        'fk_user_accounts',
        'accounts',
        type_='foreignkey'
    )
