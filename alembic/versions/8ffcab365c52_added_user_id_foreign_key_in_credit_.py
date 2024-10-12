"""Added user id foreign key in credit account table

Revision ID: 8ffcab365c52
Revises: 254b1502f619
Create Date: 2024-10-11 18:13:43.742986

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8ffcab365c52'
down_revision: Union[str, None] = '254b1502f619'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        table_name='credit_account',
        column=sa.Column(
            'user_id',
            sa.UUID(as_uuid=True), 
            nullable=False,
            server_default=sa.text('\'3d880d2b-94fc-4c89-b780-76526282774a\'')
        )
    )
    op.create_foreign_key(
        constraint_name='credit_account_user_fk',
        source_table='credit_account',
        referent_table='users',
        local_cols=['user_id'],
        remote_cols=['id']
    )

def downgrade() -> None:
    op.drop_column(
        table_name='credit_account',
        column_name='user_id'
    )
    op.drop_constraint(
        constraint_name='credit_account_user_fk',
        table_name='credit_account',
        type_='foreignkey'
    )
