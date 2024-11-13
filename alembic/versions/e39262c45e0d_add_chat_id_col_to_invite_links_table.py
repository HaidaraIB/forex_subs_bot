"""add chat_id col to invite_links table

Revision ID: e39262c45e0d
Revises: 
Create Date: 2024-11-10 12:36:58.183842

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e39262c45e0d"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("invite_links") as batch_op:
        batch_op.add_column(
            sa.Column(
                name="chat_id",
                type_=sa.Integer,
                server_default='-1002392883539'
            )
        )


def downgrade() -> None:
    with op.batch_alter_table("invite_links") as batch_op:
        batch_op.drop_column("chat_id")
