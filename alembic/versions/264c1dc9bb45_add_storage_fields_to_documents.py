"""add storage fields to documents

Revision ID: 264c1dc9bb45
Revises: d783f01cc1e3
Create Date: 2026-08-21 23:19:00.716739

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '264c1dc9bb45'
down_revision: Union[str, Sequence[str], None] = 'd783f01cc1e3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('documents', sa.Column('storage_public_id', sa.String(length=255), nullable=True))
    op.add_column('documents', sa.Column('file_url', sa.String(length=512), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('documents', 'file_url')
    op.drop_column('documents', 'storage_public_id')
