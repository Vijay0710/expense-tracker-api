"""Add Billing Cycle Column in Credit Card Table

Revision ID: 254b1502f619
Revises: 9fc1a6779568
Create Date: 2024-10-11 17:28:22.482043

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '254b1502f619'
down_revision: Union[str, None] = '9fc1a6779568'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        table_name='credit_account',
        column=sa.Column('billing_cycle', sa.String(), nullable=False)
    )

    op.add_column(
        table_name='credit_account',
        column=sa.Column('total_reward_points', sa.String(), nullable=False)
    )


def downgrade() -> None:
    op.drop_column(
        table_name='credit_account',
        column_name='billing_cycle'
    )

    op.drop_column(
        table_name='credit_account',
        column_name='total_reward_points'
    )
