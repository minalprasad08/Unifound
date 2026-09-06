"""add_image_analysis_to_items

Revision ID: 28a1c9e4b7d3
Revises: 12f670798e8b
Create Date: 2026-09-03 22:15:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '28a1c9e4b7d3'
down_revision: Union[str, None] = '12f670798e8b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('items', sa.Column('image_analysis', sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column('items', 'image_analysis')
