"""prescription per set: surrogate id + prescribed_set table

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-08-18 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d4e5f6a7b8c9"
down_revision: Union[str, None] = "c3d4e5f6a7b8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Prescription moves from three scalar columns to an ordered child table, so
    # training_unit_exercise needs a single-column surrogate PK to be FK-referenced.
    op.drop_column("training_unit_exercise", "sets")
    op.drop_column("training_unit_exercise", "reps")
    op.drop_column("training_unit_exercise", "weight")

    op.drop_constraint(
        "training_unit_exercise_pkey", "training_unit_exercise", type_="primary"
    )
    op.add_column(
        "training_unit_exercise",
        sa.Column("id", sa.Integer(), sa.Identity(always=False), nullable=False),
    )
    op.create_primary_key(
        "training_unit_exercise_pkey", "training_unit_exercise", ["id"]
    )
    op.create_unique_constraint(
        "training_unit_exercise_training_unit_id_key",
        "training_unit_exercise",
        ["training_unit_id", "exercise_id"],
    )

    op.create_table(
        "prescribed_set",
        sa.Column("id", sa.Integer(), sa.Identity(always=False), nullable=False),
        sa.Column("training_unit_exercise_id", sa.Integer(), nullable=False),
        sa.Column("set_number", sa.Integer(), nullable=False),
        sa.Column("reps", sa.Integer(), nullable=True),
        sa.Column("weight", sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(
            ["training_unit_exercise_id"],
            ["training_unit_exercise.id"],
            name="prescribed_set_training_unit_exercise_id_fkey",
        ),
        sa.PrimaryKeyConstraint("id", name="prescribed_set_pkey"),
    )
    op.create_index(
        "prescribed_set_training_unit_exercise_id_idx",
        "prescribed_set",
        ["training_unit_exercise_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "prescribed_set_training_unit_exercise_id_idx", table_name="prescribed_set"
    )
    op.drop_table("prescribed_set")

    op.drop_constraint(
        "training_unit_exercise_training_unit_id_key",
        "training_unit_exercise",
        type_="unique",
    )
    op.drop_constraint(
        "training_unit_exercise_pkey", "training_unit_exercise", type_="primary"
    )
    op.drop_column("training_unit_exercise", "id")
    op.create_primary_key(
        "training_unit_exercise_pkey",
        "training_unit_exercise",
        ["training_unit_id", "exercise_id"],
    )

    op.add_column(
        "training_unit_exercise", sa.Column("sets", sa.Integer(), nullable=True)
    )
    op.add_column(
        "training_unit_exercise", sa.Column("reps", sa.Integer(), nullable=True)
    )
    op.add_column(
        "training_unit_exercise", sa.Column("weight", sa.Float(), nullable=True)
    )