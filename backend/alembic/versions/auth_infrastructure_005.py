"""Create production authentication/session/RBAC/audit tables.

The original bootstrap migration populated Base.metadata from app.db.models,
but that package did not import the authentication and audit ORM modules.
Fresh Neon databases therefore could contain users while missing the tables
needed to finish login (user_sessions, refresh_tokens, audit_logs, roles, etc.).

This migration explicitly imports those models and creates any missing tables
without modifying existing user or health data.
"""

from alembic import op

from app.db.base import Base
from app.db.models import auth_models, audit_models  # noqa: F401

revision = "auth_infrastructure_005"
down_revision = "documents_history_004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    Base.metadata.create_all(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    # Never drop authentication or audit data automatically during a downgrade.
    pass
