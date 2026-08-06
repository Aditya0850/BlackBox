"""Reserve notebook schema for human-authored content (Investigation Notebook).

Revision ID: 20260801_120002
Revises: 20260801_120001
Create Date: 2026-08-01 12:00:02

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = '20260801_120002'
down_revision = '20260801_120001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create notebook schema (reserved for human-authored content)
    op.execute(text("CREATE SCHEMA IF NOT EXISTS notebook"))

    # Grant usage to blackbox_app for future use (but not full DML - will be restricted)
    op.execute(text("GRANT USAGE ON SCHEMA notebook TO blackbox_app"))

    # Note: The pipeline worker role should NOT have any grant on notebook schema
    # This enforces the Human/Machine separation principle:
    # - AI (pipeline worker) can read intel.*, write intel.*, write audit.*
    # - AI CANNOT access notebook.* at all
    # - Humans (via application) can read/write notebook.*

    # Future tables that would go in notebook schema (not created in v1):
    # - notebook.theories
    # - notebook.theory_evidence_links
    # - notebook.investigator_notes
    # - notebook.hypotheses


def downgrade() -> None:
    # Drop notebook schema
    op.execute(text("DROP SCHEMA IF EXISTS notebook CASCADE"))