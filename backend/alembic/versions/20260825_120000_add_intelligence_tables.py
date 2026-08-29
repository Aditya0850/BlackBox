"""intelligence tables for entity/relationship storage

Revision ID: 20260825_120000
Revises: 20260806_120000
Create Date: 2026-08-25 12:00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = '20260825_120000'
down_revision = '20260806_120000'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create intel.entities table
    op.create_table(
        'entities',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True, default=sa.text('uuid_generate_v4()')),
        sa.Column('case_id', sa.UUID(as_uuid=True), sa.ForeignKey('intel.cases.id'), nullable=False),
        sa.Column('entity_type', sa.String(20), nullable=False),
        sa.Column('canonical_value', sa.Text, nullable=False),
        sa.Column('normalized_key', sa.String(255), nullable=False),
        sa.Column('entity_metadata', sa.JSON, nullable=True),
        sa.Column('resolution_confidence', sa.Float, nullable=False, default=0.0),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.UniqueConstraint('case_id', 'entity_type', 'normalized_key', name='uq_entities_case_type_normalized_key'),
        schema='intel'
    )
    
    # Create indexes for entities
    op.create_index('idx_entities_case_type', 'entities', ['case_id', 'entity_type'], schema='intel')
    op.create_index('idx_entities_normalized_key', 'entities', ['normalized_key'], schema='intel')
    
    # Create intel.entity_mentions table
    op.create_table(
        'entity_mentions',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True, default=sa.text('uuid_generate_v4()')),
        sa.Column('entity_id', sa.UUID(as_uuid=True), sa.ForeignKey('intel.entities.id'), nullable=False),
        sa.Column('finding_id', sa.UUID(as_uuid=True), sa.ForeignKey('intel.findings.id'), nullable=False),
        sa.Column('source_text', sa.Text, nullable=False),
        sa.Column('text_start_offset', sa.Integer, nullable=False),
        sa.Column('text_end_offset', sa.Integer, nullable=False),
        sa.Column('confidence_score', sa.Float, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        schema='intel'
    )
    
    # Create indexes for entity_mentions
    op.create_index('idx_mentions_entity', 'entity_mentions', ['entity_id'], schema='intel')
    op.create_index('idx_mentions_finding', 'entity_mentions', ['finding_id'], schema='intel')
    
    # Create intel.relationships table
    op.create_table(
        'relationships',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True, default=sa.text('uuid_generate_v4()')),
        sa.Column('case_id', sa.UUID(as_uuid=True), sa.ForeignKey('intel.cases.id'), nullable=False),
        sa.Column('subject_entity_id', sa.UUID(as_uuid=True), sa.ForeignKey('intel.entities.id'), nullable=False),
        sa.Column('predicate', sa.String(50), nullable=False),
        sa.Column('object_entity_id', sa.UUID(as_uuid=True), sa.ForeignKey('intel.entities.id'), nullable=False),
        sa.Column('confidence_score', sa.Float, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        schema='intel'
    )
    
    # Create indexes for relationships
    op.create_index('idx_relationships_case', 'relationships', ['case_id'], schema='intel')
    
    # Create intel.relationship_evidence table
    op.create_table(
        'relationship_evidence',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True, default=sa.text('uuid_generate_v4()')),
        sa.Column('relationship_id', sa.UUID(as_uuid=True), sa.ForeignKey('intel.relationships.id'), nullable=False),
        sa.Column('finding_id', sa.UUID(as_uuid=True), sa.ForeignKey('intel.findings.id'), nullable=False),
        sa.Column('source_text', sa.Text, nullable=False),
        sa.Column('text_start_offset', sa.Integer, nullable=False),
        sa.Column('text_end_offset', sa.Integer, nullable=False),
        sa.Column('confidence_score', sa.Float, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        schema='intel'
    )
    
    # Create indexes for relationship_evidence
    op.create_index('idx_relationship_evidence_rel', 'relationship_evidence', ['relationship_id'], schema='intel')
    
    # Create intel.pattern_findings table
    op.create_table(
        'pattern_findings',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True, default=sa.text('uuid_generate_v4()')),
        sa.Column('case_id', sa.UUID(as_uuid=True), sa.ForeignKey('intel.cases.id'), nullable=False),
        sa.Column('pattern_type', sa.String(50), nullable=False),
        sa.Column('description', sa.Text, nullable=False),
        sa.Column('entities_involved', sa.JSON, nullable=False),
        sa.Column('evidence_trail', sa.JSON, nullable=False),
        sa.Column('confidence_score', sa.Float, nullable=False),
        sa.Column('detected_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        schema='intel'
    )
    
    # Create indexes for pattern_findings
    op.create_index('idx_pattern_findings_case', 'pattern_findings', ['case_id'], schema='intel')
    
    # Grant privileges on new tables to blackbox_app
    op.execute(text("GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA intel TO blackbox_app"))


def downgrade() -> None:
    # Drop tables in reverse order due to foreign key constraints
    op.drop_table('pattern_findings', schema='intel')
    op.drop_table('relationship_evidence', schema='intel')
    op.drop_table('relationships', schema='intel')
    op.drop_table('entity_mentions', schema='intel')
    op.drop_table('entities', schema='intel')
    
    # Revoke privileges
    op.execute(text("REVOKE ALL ON ALL TABLES IN SCHEMA intel FROM blackbox_app"))
