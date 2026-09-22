"""Ensure patient history/document/reminder tables and indexes exist.

The bootstrap migration creates ORM-managed tables. This follow-up migration
repairs partially-created databases as well: existing tables are preserved,
missing ORM indexes are created, and nothing is destructively dropped.
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
        if table is None:
            continue

        # Create the table only when it is genuinely absent.
        table.create(bind=bind, checkfirst=True)

        # A previous version of this migration could create the table but fail
        # while creating an index. Create each metadata index independently so
        # a partially-applied database is repaired on the next deployment.
        for index in table.indexes:
            index.create(bind=bind, checkfirst=True)


def downgrade() -> None:
    # Never destroy patient/biomarker data as part of a migration rollback.
    pass
