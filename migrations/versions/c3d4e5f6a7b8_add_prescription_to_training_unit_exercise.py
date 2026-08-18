"""add prescription to training_unit_exercise

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-08-17 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c3d4e5f6a7b8"
down_revision: Union[str, None] = "b2c3d4e5f6a7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Prescription is optional per link -> all three columns are nullable.
    op.add_column(
        "training_unit_exercise", sa.Column("sets", sa.Integer(), nullable=True)
    )
    op.add_column(
        "training_unit_exercise", sa.Column("reps", sa.Integer(), nullable=True)
    )
    op.add_column(
        "training_unit_exercise", sa.Column("weight", sa.Float(), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("training_unit_exercise", "weight")
    op.drop_column("training_unit_exercise", "reps")
    op.drop_column("training_unit_exercise", "sets")