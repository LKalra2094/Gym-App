"""make exercise log weight_unit not-nullable

Revision ID: 55b733f4ba95
Revises: beca26b5f906
Create Date: 2025-06-23 23:09:35.056042

"""
from typing import Union
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '55b733f4ba95'
down_revision: str | None = 'beca26b5f906'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # Backfill existing NULL values with a default, casting to the enum type
    op.execute("UPDATE exercise_logs SET weight_unit = 'KG'::weightunit WHERE weight_unit IS NULL")
    
    # Now, apply the NOT NULL constraint
    op.alter_column('exercise_logs', 'weight_unit',
               existing_type=sa.VARCHAR(length=3),
               nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Revert the NOT NULL constraint
    op.alter_column('exercise_logs', 'weight_unit',
               existing_type=sa.Enum('KG', 'LBS', name='weightunit'),
               nullable=True)
    # The backfill is not reversible, no action needed here.
    pass
