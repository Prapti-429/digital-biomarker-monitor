"""Bootstrap and repair the production SQLAlchemy schema.

The project originally created tables from FastAPI startup. This migration
moves schema ownership to Alembic and repairs the two known historical user
foreign keys that were created as INTEGER instead of UUID.
"""

from alembic import op
from sqlalchemy import text

from app.db.base import Base
from app.db import models  # noqa: F401 - populate Base.metadata

revision = "bootstrap_schema_002"
down_revision = "fix_fk_uuid_001"
branch_labels = None
depends_on = None


def _repair_user_fk(table: str, column: str, constraint: str) -> None:
    """Convert a legacy INTEGER user FK to UUID when that legacy schema exists."""
    bind = op.get_bind()
    result = bind.execute(
        text(
            """
            SELECT data_type
            FROM information_schema.columns
            WHERE table_schema = current_schema()
              AND table_name = :table
              AND column_name = :column
            """
        ),
        {"table": table, "column": column},
    ).scalar()

    if result == "integer":
        # Legacy prototype rows cannot contain a meaningful UUID representation
        # of an integer user id. Preserve the row but clear this optional
        # attribution field before changing its type.
        op.execute(f'ALTER TABLE "{table}" DROP CONSTRAINT IF EXISTS "{constraint}"')
        op.execute(
            f'ALTER TABLE "{table}" ALTER COLUMN "{column}" TYPE uuid USING NULL::uuid'
        )
        op.execute(
            f'ALTER TABLE "{table}" ADD CONSTRAINT "{constraint}" '
            f'FOREIGN KEY ("{column}") REFERENCES users(id) ON DELETE SET NULL'
        )


def upgrade() -> None:
    _repair_user_fk(
        "medication_regimens",
        "prescribing_clinician_id",
        "medication_regimens_prescribing_clinician_id_fkey",
    )
    _repair_user_fk(
        "file_upload_records",
        "uploaded_by_user_id",
        "file_upload_records_uploaded_by_user_id_fkey",
    )

    # Create every missing table using the current UUID-consistent ORM metadata.
    # Existing tables are preserved.
    Base.metadata.create_all(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    # Never destroy patient/biomarker data as part of a migration rollback.
    pass
