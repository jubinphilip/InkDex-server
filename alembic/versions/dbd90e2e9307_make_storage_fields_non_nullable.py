"""make storage fields non nullable

Revision ID: dbd90e2e9307
Revises: 264c1dc9bb45
Create Date: 2026-08-21 23:23:02.915993

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dbd90e2e9307'
down_revision: Union[str, Sequence[str], None] = '264c1dc9bb45'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column('documents', 'storage_public_id', existing_type=sa.String(length=255), nullable=False)
    op.alter_column('documents', 'file_url', existing_type=sa.String(length=512), nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column('documents', 'file_url', existing_type=sa.String(length=512), nullable=True)
    op.alter_column('documents', 'storage_public_id', existing_type=sa.String(length=255), nullable=True)
