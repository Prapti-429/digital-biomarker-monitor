"""Add continuity rewards for consistent daily check-ins.

Rewards are a non-medical engagement feature. They recognize completion
of a NUVYRA check-in, never medication use or a medical outcome.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision = "continuity_rewards_003"
down_revision = "bootstrap_schema_002"
branch_labels = None
depends_on = None


def _add_column_if_missing(column_name: str, column: sa.Column) -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    existing = {item["name"] for item in inspector.get_columns("users")}
    if column_name not in existing:
        op.add_column("users", column)


def upgrade() -> None:
    _add_column_if_missing(
        "reward_coins",
        sa.Column("reward_coins", sa.Integer(), nullable=False, server_default="0"),
    )
    _add_column_if_missing(
        "reward_streak",
        sa.Column("reward_streak", sa.Integer(), nullable=False, server_default="0"),
    )
    _add_column_if_missing(
        "reward_last_check_in_date",
        sa.Column("reward_last_check_in_date", sa.DateTime(timezone=True), nullable=True),
    )

    # Remove temporary migration defaults after existing rows have been
    # backfilled. This is safe to repeat on an already-correct schema.
    op.alter_column("users", "reward_coins", server_default=None)
    op.alter_column("users", "reward_streak", server_default=None)


def downgrade() -> None:
    # Rollback remains intentionally conservative: only remove columns that
    # this migration owns, and tolerate a partially-applied migration.
    bind = op.get_bind()
    inspector = inspect(bind)
    existing = {item["name"] for item in inspector.get_columns("users")}

    for column_name in (
        "reward_last_check_in_date",
        "reward_streak",
        "reward_coins",
    ):
        if column_name in existing:
            op.drop_column("users", column_name)
