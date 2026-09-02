"""add_status_to_documents

Revision ID: b1ec432b0e54
Revises: dbd90e2e9307
Create Date: 2026-09-02 22:36:36.093694

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b1ec432b0e54'
down_revision: Union[str, Sequence[str], None] = 'dbd90e2e9307'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('documents', sa.Column('status', sa.String(length=50), nullable=False, server_default='processing'))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('documents', 'status')
