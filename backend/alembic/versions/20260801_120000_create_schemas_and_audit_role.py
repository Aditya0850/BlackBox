"""create schemas and audit role

Revision ID: 20260801_120000
Revises:
Create Date: 2026-08-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = '20260801_120000'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create schemas
    op.execute(text("CREATE SCHEMA IF NOT EXISTS intel"))
    op.execute(text("CREATE SCHEMA IF NOT EXISTS audit"))

    # Create a role for the application to use (will be refined later)
    op.execute(text("DO $$ BEGIN IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'blackbox_app') THEN CREATE ROLE blackbox_app LOGIN PASSWORD 'blackbox_app_password'; END IF; END $$;"))
    op.execute(text("GRANT USAGE ON SCHEMA intel TO blackbox_app"))
    op.execute(text("GRANT USAGE ON SCHEMA audit TO blackbox_app"))

    # Create a role for audit writes (will be refined later when we have the audit.events table)
    op.execute(text("DO $$ BEGIN IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'audit_writer') THEN CREATE ROLE audit_writer LOGIN PASSWORD 'audit_writer_password'; END IF; END $$;"))
    op.execute(text("GRANT USAGE ON SCHEMA audit TO audit_writer"))


def downgrade() -> None:
    # Drop roles
    op.execute(text("DROP ROLE IF EXISTS audit_writer"))
    op.execute(text("DROP ROLE IF EXISTS blackbox_app"))
    # Drop schemas
    op.execute(text("DROP SCHEMA IF EXISTS audit CASCADE"))
    op.execute(text("DROP SCHEMA IF EXISTS intel CASCADE"))