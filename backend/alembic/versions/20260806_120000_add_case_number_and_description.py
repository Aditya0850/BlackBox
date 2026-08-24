"""add case_number and description to cases table

Revision ID: 20260806_120000
Revises: 20260801_120002
Create Date: 2026-08-06 12:00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = '20260806_120000'
down_revision = '20260801_120002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new columns to intel.cases
    op.add_column(
        'cases',
        sa.Column('case_number', sa.String(20), nullable=True),
        schema='intel'
    )
    op.add_column(
        'cases',
        sa.Column('description', sa.Text, nullable=False, server_default=''),
        schema='intel'
    )

    # Create sequence for case number generation (per year)
    op.execute(text("CREATE SEQUENCE intel.case_number_seq"))

    # Function to generate next case number
    op.execute(text("""
        CREATE OR REPLACE FUNCTION intel.next_case_number() RETURNS VARCHAR(20) AS $$
        DECLARE
            yr INT := EXTRACT(YEAR FROM CURRENT_DATE);
            seq INT;
        BEGIN
            -- Get next sequence value
            seq := nextval('intel.case_number_seq');
            RETURN 'CASE-' || yr || '-' || lpad(seq::text, 5, '0');
        END;
        $$ LANGUAGE plpgsql;
    """))

    # Backfill existing rows with generated case numbers
    op.execute(text("UPDATE intel.cases SET case_number = intel.next_case_number() WHERE case_number IS NULL"))

    # Now make case_number NOT NULL
    op.alter_column('cases', 'case_number', nullable=False, schema='intel')

    # Create unique index on case_number
    op.create_index('idx_cases_case_number', 'cases', ['case_number'], schema='intel', unique=True)

    # Grant usage on sequence to blackbox_app
    op.execute(text("GRANT USAGE, SELECT ON SEQUENCE intel.case_number_seq TO blackbox_app"))


def downgrade() -> None:
    # Revoke permissions
    op.execute(text("REVOKE ALL ON SEQUENCE intel.case_number_seq FROM blackbox_app"))

    # Drop index
    op.drop_index('idx_cases_case_number', table_name='cases', schema='intel')

    # Drop function and sequence
    op.execute(text("DROP FUNCTION IF EXISTS intel.next_case_number()"))
    op.execute(text("DROP SEQUENCE IF EXISTS intel.case_number_seq"))

    # Drop columns
    op.drop_column('cases', 'description', schema='intel')
    op.drop_column('cases', 'case_number', schema='intel')