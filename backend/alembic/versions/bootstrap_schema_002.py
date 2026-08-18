"""Bootstrap the SQLAlchemy schema for the production prototype.

The project originally used ``Base.metadata.create_all`` during FastAPI
startup. That made Render deployments vulnerable to model/schema drift and
foreign-key type mismatches. Schema creation is now owned by Alembic.

This migration is intentionally idempotent through SQLAlchemy's create_all:
it creates any missing tables from the current, UUID-consistent ORM metadata
without dropping existing data.
"""

from alembic import op

from app.db.base import Base
from app.db import models  # noqa: F401 - populate Base.metadata

revision = "bootstrap_schema_002"
down_revision = "fix_fk_uuid_001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    Base.metadata.create_all(bind=bind, checkfirst=True)


def downgrade() -> None:
    # Schema is intentionally not destroyed by a downgrade of the bootstrap
    # revision. Data-destructive teardown should be an explicit database task.
    pass
