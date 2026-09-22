"""Ensure patient history/document/reminder tables exist.

The bootstrap migration already creates ORM-managed tables. This follow-up
migration is intentionally idempotent and uses the same SQLAlchemy metadata
as the application, avoiding duplicate/manual index definitions.
"""

from alembic import op

from app.db.base import Base
from app.db import models  # noqa: F401 - register all ORM models


revision = "documents_history_004"
down_revision = "continuity_rewards_003"
branch_labels = None
depends_on = None


TABLES = (
    "past_history_records",
    "medical_documents",
    "health_reminders",
)


def upgrade() -> None:
    bind = op.get_bind()

    for table_name in TABLES:
        table = Base.metadata.tables.get(table_name)
        if table is not None:
            # checkfirst makes this safe when bootstrap_schema_002 already
            # created the table, while also repairing databases where it is
            # genuinely missing.
            table.create(bind=bind, checkfirst=True)


def downgrade() -> None:
    # Keep patient data safe. Schema rollback is intentionally non-destructive.
    pass
