"""Add continuity rewards for consistent daily check-ins.

Rewards are a non-medical engagement feature. They recognize completion
of a NUVYRA check-in, never medication use or a medical outcome.
"""

from alembic import op
import sqlalchemy as sa

revision = "continuity_rewards_003"
down_revision = "bootstrap_schema_002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("reward_coins", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("users", sa.Column("reward_streak", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("users", sa.Column("reward_last_check_in_date", sa.DateTime(timezone=True), nullable=True))
    op.alter_column("users", "reward_coins", server_default=None)
    op.alter_column("users", "reward_streak", server_default=None)


def downgrade() -> None:
    op.drop_column("users", "reward_last_check_in_date")
    op.drop_column("users", "reward_streak")
    op.drop_column("users", "reward_coins")
