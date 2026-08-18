"""fix patient profile foreign keys to uuid

Revision ID: fix_fk_uuid_001
Revises: 
Create Date: 2026-08-18 19:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'fix_fk_uuid_001'
down_revision = None  # Put your previous revision ID here if one exists
branch_labels = None
depends_on = None


def upgrade():
    # Drop existing incompatible foreign key constraints
    op.execute("ALTER TABLE patient_profiles DROP CONSTRAINT IF EXISTS patient_profiles_user_id_fkey")
    op.execute("ALTER TABLE patient_profiles DROP CONSTRAINT IF EXISTS patient_profiles_treating_physician_id_fkey")

    # Safely cast integer columns to UUID (or re-create type)
    op.execute("ALTER TABLE patient_profiles ALTER COLUMN user_id TYPE UUID USING user_id::text::uuid")
    op.execute("ALTER TABLE patient_profiles ALTER COLUMN treating_physician_id TYPE UUID USING treating_physician_id::text::uuid")

    # Re-create the matching foreign key constraints
    op.create_foreign_key(
        "patient_profiles_user_id_fkey",
        "patient_profiles",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "patient_profiles_treating_physician_id_fkey",
        "patient_profiles",
        "users",
        ["treating_physician_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade():
    op.drop_constraint("patient_profiles_user_id_fkey", "patient_profiles", type_="foreignkey")
    op.drop_constraint("patient_profiles_treating_physician_id_fkey", "patient_profiles", type_="foreignkey")