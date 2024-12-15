"""add created_at col to invite_links table

Revision ID: 067d62a86134
Revises: e39262c45e0d
Create Date: 2024-11-29 19:16:59.051238

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import datetime
from dateutil import tz

# revision identifiers, used by Alembic.
revision: str = "067d62a86134"
down_revision: Union[str, None] = "e39262c45e0d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    try:
        with op.batch_alter_table("invite_links") as batch_op:
            batch_op.add_column(
                sa.Column(
                    name="created_at",
                    type_=sa.TIMESTAMP,
                    server_default=str(
                        datetime.datetime.now(tz.gettz("Asia/Riyadh")),
                    ),
                )
            )
    except:
        pass


def downgrade() -> None:
    try:
        with op.batch_alter_table("invite_links") as batch_op:
            batch_op.drop_column(
                column_name="created_at",
            )
    except:
        pass
