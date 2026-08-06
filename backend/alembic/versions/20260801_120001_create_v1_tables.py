"""create v1 tables - cases, evidence, case_evidence, analysis_snapshots, findings, audit.events

Revision ID: 20260801_120001
Revises: 20260801_120000
Create Date: 2026-08-01 12:00:01

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY, INET

# revision identifiers, used by Alembic.
revision = '20260801_120001'
down_revision = '20260801_120000'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create intel.cases table
    op.create_table(
        'cases',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=text('gen_random_uuid()')),
        sa.Column('title', sa.Text, nullable=False),
        sa.Column('status', sa.Text, nullable=False),
        sa.Column('created_by', UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('closed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('archived_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('tags', ARRAY(sa.Text), nullable=False, server_default='{}'),
        sa.CheckConstraint("status IN ('open','closed','archived')", name='ck_cases_status'),
        schema='intel',
    )
    op.create_index('idx_cases_status', 'cases', ['status'], schema='intel')
    op.create_index('idx_cases_tags', 'cases', ['tags'], schema='intel', postgresql_using='gin')

    # Create intel.evidence table
    op.create_table(
        'evidence',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=text('gen_random_uuid()')),
        sa.Column('original_filename', sa.Text, nullable=False),
        sa.Column('mime_type', sa.Text, nullable=False),
        sa.Column('file_size_bytes', sa.BigInteger, nullable=False),
        sa.Column('sha256_hash', sa.String(64), nullable=False, unique=True),
        sa.Column('storage_location', sa.Text, nullable=False),
        sa.Column('uploaded_by', UUID(as_uuid=True), nullable=False),
        sa.Column('uploaded_at', sa.DateTime(timezone=True), nullable=False, server_default=text('now()')),
        schema='intel',
    )
    op.create_index('idx_evidence_hash', 'evidence', ['sha256_hash'], schema='intel', unique=True)

    # Create intel.case_evidence table (many-to-many)
    op.create_table(
        'case_evidence',
        sa.Column('case_id', UUID(as_uuid=True), sa.ForeignKey('intel.cases.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('evidence_id', UUID(as_uuid=True), sa.ForeignKey('intel.evidence.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('linked_by', UUID(as_uuid=True), nullable=False),
        sa.Column('linked_at', sa.DateTime(timezone=True), nullable=False, server_default=text('now()')),
        schema='intel',
    )

    # Create intel.analysis_snapshots table
    op.create_table(
        'analysis_snapshots',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=text('gen_random_uuid()')),
        sa.Column('evidence_id', UUID(as_uuid=True), sa.ForeignKey('intel.evidence.id', ondelete='CASCADE'), nullable=False),
        sa.Column('pipeline_version', sa.Text, nullable=False),
        sa.Column('plugin_versions', JSONB, nullable=False, server_default='{}'),
        sa.Column('trigger', sa.Text, nullable=False),
        sa.Column('triggered_by', UUID(as_uuid=True), nullable=True),
        sa.Column('is_current', sa.Boolean, nullable=False, server_default=text('true')),
        sa.Column('superseded_by', UUID(as_uuid=True), nullable=True),
        sa.Column('investigator_approval', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=text('now()')),
        sa.CheckConstraint(
            "trigger IN ('upload','manual_reanalysis','scheduled_reanalysis')",
            name='ck_snapshot_trigger'
        ),
        sa.CheckConstraint(
            "investigator_approval IN ('pending','approved','rejected')",
            name='ck_snapshot_approval'
        ),
        schema='intel',
    )
    op.create_index('idx_snapshot_evidence', 'analysis_snapshots', ['evidence_id'], schema='intel')
    op.create_index(
        'idx_snapshot_current',
        'analysis_snapshots',
        ['evidence_id'],
        schema='intel',
        unique=True,
        postgresql_where=text('is_current')
    )

    # Create intel.findings table
    op.create_table(
        'findings',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=text('gen_random_uuid()')),
        sa.Column('snapshot_id', UUID(as_uuid=True), sa.ForeignKey('intel.analysis_snapshots.id', ondelete='CASCADE'), nullable=False),
        sa.Column('key', sa.String(255), nullable=False),
        sa.Column('value', JSONB, nullable=False),
        sa.Column('confidence_level', sa.Text, nullable=False),
        sa.Column('confidence_score', sa.REAL, nullable=False),
        sa.Column('extraction_method', sa.String(100), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=text('now()')),
        sa.CheckConstraint(
            "confidence_level IN ('high','medium','low','unknown')",
            name='ck_findings_confidence'
        ),
        schema='intel',
    )
    op.create_index('idx_findings_snapshot', 'findings', ['snapshot_id'], schema='intel')

    # Create audit.events table
    op.create_table(
        'events',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=text('gen_random_uuid()')),
        sa.Column('user_id', UUID(as_uuid=True), nullable=True),
        sa.Column('evidence_id', UUID(as_uuid=True), sa.ForeignKey('intel.evidence.id', ondelete='SET NULL'), nullable=True),
        sa.Column('case_id', UUID(as_uuid=True), sa.ForeignKey('intel.cases.id', ondelete='SET NULL'), nullable=True),
        sa.Column('action', sa.Text, nullable=False),
        sa.Column('previous_state', JSONB, nullable=True),
        sa.Column('new_state', JSONB, nullable=True),
        sa.Column('reason', sa.Text, nullable=True),
        sa.Column('session_id', sa.Text, nullable=True),
        sa.Column('ip_address', INET, nullable=True),
        sa.Column('device_info', sa.Text, nullable=True),
        sa.Column('ai_pipeline_version', sa.Text, nullable=True),
        sa.Column('occurred_at', sa.DateTime(timezone=True), nullable=False, server_default=text('now()')),
        schema='audit',
    )
    op.create_index('idx_audit_evidence', 'events', ['evidence_id'], schema='audit')
    op.create_index('idx_audit_case', 'events', ['case_id'], schema='audit')
    op.create_index('idx_audit_occurred', 'events', ['occurred_at'], schema='audit')

    # Grant permissions to blackbox_app role
    op.execute(text("GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA intel TO blackbox_app"))
    op.execute(text("GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA intel TO blackbox_app"))

    # Grant INSERT/SELECT only to audit_writer role (no UPDATE/DELETE)
    op.execute(text("GRANT INSERT, SELECT ON ALL TABLES IN SCHEMA audit TO audit_writer"))
    op.execute(text("GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA audit TO audit_writer"))

    # Also grant blackbox_app the ability to write audit events (for application use)
    op.execute(text("GRANT INSERT, SELECT ON ALL TABLES IN SCHEMA audit TO blackbox_app"))


def downgrade() -> None:
    # Revoke permissions
    op.execute(text("REVOKE ALL ON ALL TABLES IN SCHEMA audit FROM blackbox_app"))
    op.execute(text("REVOKE ALL ON ALL TABLES IN SCHEMA audit FROM audit_writer"))
    op.execute(text("REVOKE ALL ON ALL TABLES IN SCHEMA intel FROM blackbox_app"))

    # Drop tables in reverse order
    op.drop_table('events', schema='audit')
    op.drop_table('findings', schema='intel')
    op.drop_table('analysis_snapshots', schema='intel')
    op.drop_table('case_evidence', schema='intel')
    op.drop_table('evidence', schema='intel')
    op.drop_table('cases', schema='intel')