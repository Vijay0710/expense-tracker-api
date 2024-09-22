"""Create hashed password column for user

Revision ID: c110b9256071
Revises: 
Create Date: 2024-09-22 22:27:15.596204

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c110b9256071'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        table_name='users',
        column=sa.Column('hashed_password', sa.String())
    )


def downgrade() -> None:
    op.drop_column(
        table_name='users',
        column_name='hashed_password'
    )
