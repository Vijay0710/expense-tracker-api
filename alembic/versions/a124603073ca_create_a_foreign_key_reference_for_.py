"""Create a Foreign Key reference for Address Table

Revision ID: a124603073ca
Revises: 39ce2e906de3
Create Date: 2024-11-30 14:10:48.927505

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a124603073ca'
down_revision: Union[str, None] = '39ce2e906de3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        table_name='address',
        column=sa.Column(
            name='user_id',            
            type_=sa.UUID(as_uuid=True), 
            nullable=False,
            server_default=sa.text('\'3d880d2b-94fc-4c89-b780-76526282774a\'')
        )
    )

    op.create_foreign_key(
        constraint_name='address_user_fk',
        source_table='address',
        referent_table='users',
        local_cols=['user_id'],
        remote_cols=['id']
    )


def downgrade() -> None:
    op.drop_column(
        table_name='address',
        column_name='user_id'
    )
    op.drop_constraint(
        constraint_name='address_user_fk',
        table_name='address',
        type_='foreignkey'
    )
