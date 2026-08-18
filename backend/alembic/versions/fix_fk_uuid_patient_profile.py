"""Baseline compatibility revision.

The application currently initializes its SQLAlchemy schema with Base.metadata.create_all
at startup. This revision intentionally performs no DDL; it keeps the existing Render
start command (alembic upgrade head && uvicorn ...) safe on a fresh database.
"""

revision = "fix_fk_uuid_001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
