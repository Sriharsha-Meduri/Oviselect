"""Create cutoffs table

Revision ID: 001
Revises: None
Create Date: 2026-03-29
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "cutoffs",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("year", sa.Integer, nullable=False),
        sa.Column("round", sa.Integer, nullable=False),
        sa.Column("institute", sa.Text, nullable=False),
        sa.Column("program", sa.Text, nullable=False),
        sa.Column("quota", sa.Text, nullable=False),
        sa.Column("seat_type", sa.Text, nullable=False),
        sa.Column("opening_rank", sa.Integer, nullable=True),
        sa.Column("closing_rank", sa.Integer, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    # Unique constraint — prevents duplicate ingestion
    op.create_unique_constraint(
        "uq_cutoff_row",
        "cutoffs",
        ["year", "round", "institute", "program", "quota", "seat_type"],
    )

    # Performance indexes
    op.create_index("ix_cutoffs_institute_year_round", "cutoffs", ["institute", "year", "round"])
    op.create_index("ix_cutoffs_program_year", "cutoffs", ["program", "year"])
    op.create_index("ix_cutoffs_closing_rank", "cutoffs", ["closing_rank"])


def downgrade() -> None:
    op.drop_index("ix_cutoffs_closing_rank", table_name="cutoffs")
    op.drop_index("ix_cutoffs_program_year", table_name="cutoffs")
    op.drop_index("ix_cutoffs_institute_year_round", table_name="cutoffs")
    op.drop_constraint("uq_cutoff_row", "cutoffs", type_="unique")
    op.drop_table("cutoffs")

