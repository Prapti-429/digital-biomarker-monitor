"""Add document intelligence and past-history tables.

These tables are owned by Alembic so production startup does not depend on
SQLAlchemy create_all or schema drift.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "documents_history_004"
down_revision = "continuity_rewards_003"
branch_labels = None
depends_on = None


def _table_exists(inspector, name: str) -> bool:
    return name in inspector.get_table_names()


def _index_exists(inspector, table: str, index_name: str) -> bool:
    return any(i.get("name") == index_name for i in inspector.get_indexes(table))


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    uuid_type = postgresql.UUID(as_uuid=True)

    if not _table_exists(inspector, "past_history_records"):
        op.create_table(
            "past_history_records",
            sa.Column("id", uuid_type, primary_key=True, nullable=False),
            sa.Column("user_id", uuid_type, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
            sa.Column("illness_name", sa.String(length=255), nullable=False),
            sa.Column("details", sa.Text(), nullable=True),
            sa.Column("diagnosed_on", sa.Date(), nullable=True),
            sa.Column("current_status", sa.String(length=100), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        )

    inspector = sa.inspect(bind)
    if not _index_exists(inspector, "past_history_records", "ix_past_history_records_user_id"):
        op.create_index("ix_past_history_records_user_id", "past_history_records", ["user_id"])
    if not _index_exists(inspector, "past_history_records", "idx_history_user_created"):
        op.create_index("idx_history_user_created", "past_history_records", ["user_id", "created_at"])

    if not _table_exists(inspector, "medical_documents"):
        op.create_table(
            "medical_documents",
            sa.Column("id", uuid_type, primary_key=True, nullable=False),
            sa.Column("user_id", uuid_type, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
            sa.Column("document_type", sa.String(length=50), nullable=False),
            sa.Column("filename", sa.String(length=255), nullable=False),
            sa.Column("mime_type", sa.String(length=120), nullable=False),
            sa.Column("extracted_text", sa.Text(), nullable=True),
            sa.Column("analysis", sa.JSON(), nullable=False, server_default=sa.text("'{}'::jsonb")),
            sa.Column("uploaded_at", sa.DateTime(timezone=True), nullable=False),
        )

    inspector = sa.inspect(bind)
    if not _index_exists(inspector, "medical_documents", "ix_medical_documents_user_id"):
        op.create_index("ix_medical_documents_user_id", "medical_documents", ["user_id"])
    if not _index_exists(inspector, "ix_medical_documents_document_type"):
        op.create_index("ix_medical_documents_document_type", "medical_documents", ["document_type"])

    if not _table_exists(inspector, "health_reminders"):
        op.create_table(
            "health_reminders",
            sa.Column("id", uuid_type, primary_key=True, nullable=False),
            sa.Column("user_id", uuid_type, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
            sa.Column("title", sa.String(length=255), nullable=False),
            sa.Column("message", sa.Text(), nullable=False),
            sa.Column("due_date", sa.Date(), nullable=True),
            sa.Column("source_document_id", uuid_type, sa.ForeignKey("medical_documents.id", ondelete="SET NULL"), nullable=True),
            sa.Column("completed", sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        )

    inspector = sa.inspect(bind)
    if not _index_exists(inspector, "health_reminders", "ix_health_reminders_user_id"):
        op.create_index("ix_health_reminders_user_id", "health_reminders", ["user_id"])
    if not _index_exists(inspector, "ix_health_reminders_due_date"):
        op.create_index("ix_health_reminders_due_date", "health_reminders", ["due_date"])
    if not _index_exists(inspector, "health_reminders", "idx_reminder_user_due"):
        op.create_index("idx_reminder_user_due", "health_reminders", ["user_id", "due_date"])


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if _table_exists(inspector, "health_reminders"):
        op.drop_table("health_reminders")
    inspector = sa.inspect(bind)
    if _table_exists(inspector, "medical_documents"):
        op.drop_table("medical_documents")
    inspector = sa.inspect(bind)
    if _table_exists(inspector, "past_history_records"):
        op.drop_table("past_history_records")
