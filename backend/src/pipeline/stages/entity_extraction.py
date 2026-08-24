"""Entity extraction pipeline stage - Extracts entities and relationships from text."""
import logging
import re
from typing import Any, List, Dict, Tuple
from dataclasses import dataclass

from ...pipeline.contracts import EvidenceContext, Finding, PipelineStage, StageExecutionRecord, StageStatus
from ...domain.value_objects import ConfidenceLevel

logger = logging.getLogger(__name__)


@dataclass
class Entity:
    """Represents an extracted entity."""
    text: str
    entity_type: str  # person, location, vehicle, phone, organization
    confidence: float
    source_text: str


@dataclass
class Relationship:
    """Represents a relationship between entities."""
    subject: str
    predicate: str
    object: str
    confidence: float
    source_text: str


class EntityExtractionStage(PipelineStage):
    """Stage that extracts entities and relationships from OCR text and metadata."""
    name: str = "entity_extraction"
    model_version: str = "rule-based-v1"

    def __init__(self):
        self.model_version = "rule-based-v1"
        # Compile regex patterns for efficiency
        self._compile_patterns()

    def _compile_patterns(self):
        """Compile regex patterns for entity extraction."""
        # Phone number patterns (various formats)
        self.phone_patterns = [
            re.compile(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'),  # XXX-XXX-XXXX
            re.compile(r'\b\(\d{3}\)\s*\d{3}[-.]?\d{4}\b'),  # (XXX) XXX-XXXX
            re.compile(r'\b\d{10}\b'),  # XXXXXXXXXX
            re.compile(r'\b\d{3}\s\d{3}\s\d{4}\b'),  # XXX XXX XXXX
        ]

        # License plate patterns (common formats)
        self.vehicle_patterns = [
            re.compile(r'\b[A-Z]{1,3}\d{1,4}\b'),  # ABC123
            re.compile(r'\b\d{1,4}[A-Z]{1,3}\b'),  # 123ABC
            re.compile(r'\b[A-Z]{2}\d{2,4}[A-Z]{1,2}\b'),  # AB123CD
        ]

        # Person name patterns (simple heuristic)
        self.person_patterns = [
            re.compile(r'\b(?:Mr\.|Mrs\.|Ms\.|Dr\.|Prof\.)\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'),
            re.compile(r'\b[A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\b'),  # First Last
        ]

        # Organization patterns
        self.org_patterns = [
            re.compile(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Inc\.|LLC\.|Corp\.|Corporation|Company|Ltd\.|Limited)\b'),
            re.compile(r'\b(?:Police|Department|Agency|Bureau|Office)\s+of\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'),
            re.compile(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Station|Precinct|Division)\b'),
        ]

        # Location patterns
        self.location_patterns = [
            re.compile(r'\b\d{1,5}\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Street|St\.|Avenue|Ave\.|Road|Rd\.|Boulevard|Blvd\.|Lane|Ln\.|Drive|Dr\.|Court|Ct\.|Plaza|Pl\.)\b'),
            re.compile(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*,\s*[A-Z]{2}\s+\d{5}\b'),  # City, State ZIP
            re.compile(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:City|Town|Village)\b'),
        ]

    def run(self, context: EvidenceContext) -> EvidenceContext:
        """Extract entities and relationships from OCR text and metadata."""
        record = StageExecutionRecord(
            stage_name=self.name,
            status=StageStatus.RETRYING,
            started_at=None,
            model_version=self.model_version,
        )

        try:
            # Get OCR text from previous findings
            ocr_text = self._get_ocr_text(context)

            if not ocr_text:
                logger.info("No OCR text available for entity extraction")
                record.status = StageStatus.SKIPPED
                record.reason = "No OCR text available for entity extraction"
                return context

            # Extract entities
            entities = self._extract_entities(ocr_text)

            # Extract relationships
            relationships = self._extract_relationships(ocr_text, entities)

            # Add findings to context
            self._add_entity_findings(context, entities)
            self._add_relationship_findings(context, relationships)

            # Store extracted entities/relationships in metadata for potential later persistence
            context.metadata["extracted_entities"] = [self._entity_to_dict(e) for e in entities]
            context.metadata["extracted_relationships"] = [self._relationship_to_dict(r) for r in relationships]

            if entities or relationships:
                record.status = StageStatus.SUCCESS
                record.reason = f"Entity extraction completed: {len(entities)} entities, {len(relationships)} relationships"
            else:
                record.status = StageStatus.SUCCESS
                record.reason = "Entity extraction completed: no entities or relationships found"

        except Exception as e:
            record.status = StageStatus.FAILED
            record.error_details = str(e)
            record.reason = f"Entity extraction failed: {type(e).__name__}"
            logger.error(f"Entity extraction stage failed: {e}", exc_info=True)

            context.add_finding(Finding(
                key="entity_extraction.error",
                value={"error": str(e)},
                confidence_level=ConfidenceLevel.UNKNOWN,
                confidence_score=0.0,
                extraction_method="entity_extraction",
            ))

        return context

    def _get_ocr_text(self, context: EvidenceContext) -> str:
        """Get OCR text from previous findings."""
        ocr_findings = context.get_findings_by_key("ocr.text")
        if ocr_findings:
            latest = ocr_findings[-1]
            return latest.value.get("text", "") if isinstance(latest.value, dict) else str(latest.value)
        return ""

    def _extract_entities(self, text: str) -> List[Entity]:
        """Extract entities from text using rule-based patterns."""
        entities = []

        # Extract phone numbers
        for pattern in self.phone_patterns:
            for match in pattern.finditer(text):
                entities.append(Entity(
                    text=match.group(),
                    entity_type="phone",
                    confidence=0.8,
                    source_text=text[max(0, match.start()-20):min(len(text), match.end()+20)]
                ))

        # Extract vehicle plates
        for pattern in self.vehicle_patterns:
            for match in pattern.finditer(text):
                entities.append(Entity(
                    text=match.group(),
                    entity_type="vehicle",
                    confidence=0.7,
                    source_text=text[max(0, match.start()-20):min(len(text), match.end()+20)]
                ))

        # Extract person names
        for pattern in self.person_patterns:
            for match in pattern.finditer(text):
                # Filter out common false positives
                name = match.group().strip()
                if not self._is_false_positive_person(name):
                    entities.append(Entity(
                        text=name,
                        entity_type="person",
                        confidence=0.6,
                        source_text=text[max(0, match.start()-30):min(len(text), match.end()+30)]
                    ))

        # Extract organizations
        for pattern in self.org_patterns:
            for match in pattern.finditer(text):
                entities.append(Entity(
                    text=match.group(),
                    entity_type="organization",
                    confidence=0.7,
                    source_text=text[max(0, match.start()-30):min(len(text), match.end()+30)]
                ))

        # Extract locations
        for pattern in self.location_patterns:
            for match in pattern.finditer(text):
                entities.append(Entity(
                    text=match.group(),
                    entity_type="location",
                    confidence=0.7,
                    source_text=text[max(0, match.start()-30):min(len(text), match.end()+30)]
                ))

        # Deduplicate entities (simple approach)
        return self._deduplicate_entities(entities)

    def _is_false_positive_person(self, name: str) -> bool:
        """Check if a detected person name is likely a false positive."""
        false_positives = {
            "Street", "Avenue", "Road", "Boulevard", "Lane", "Drive", "Court", "Plaza",
            "Inc", "LLC", "Corp", "Corporation", "Company", "Ltd", "Limited",
            "Police", "Department", "Agency", "Bureau", "Office",
            "City", "Town", "Village", "State", "County"
        }

        # Check if it's just a common word
        if name in false_positives:
            return True

        # Check if it's all caps (likely an acronym, not a person name)
        if name.isupper() and len(name) > 2:
            return True

        return False

    def _extract_relationships(self, text: str, entities: List[Entity]) -> List[Relationship]:
        """Extract relationships between entities based on proximity and patterns."""
        relationships = []

        if len(entities) < 2:
            return relationships

        # Simple proximity-based relationship extraction
        # In a real implementation, this would use dependency parsing or LLM

        # Look for common relationship indicators
        relationship_indicators = [
            (r'\b(?:called|phoned|contacted|spoke\s+with|met\s+with)\b', "contacted"),
            (r'\b(?:lives\s+at|resides\s+at|address\s+is)\b', "lives_at"),
            (r'\b(?:owns|possesses|has)\b', "owns"),
            (r'\b(?:works\s+at|employed\s+by|job\s+at)\b', "works_at"),
            (r'\b(?:visited|went\s+to|was\s+at)\b', "visited"),
            (r'\b(?:saw|observed|noticed)\b', "observed"),
            (r'\b(?:driver\s+of|operator\s+of)\b', "driver_of"),
            (r'\b(?:registered\s+to|owned\s+by)\b', "registered_to"),
        ]

        # For each indicator, look for entity pairs nearby
        for pattern_str, predicate in relationship_indicators:
            pattern = re.compile(pattern_str, re.IGNORECASE)
            for match in pattern.finditer(text):
                # Find entities near this relationship indicator
                match_start, match_end = match.span()
                search_window = text[max(0, match_start-50):min(len(text), match_end+50)]

                # Find entities in the search window
                nearby_entities = [
                    e for e in entities
                    if e.text in search_window
                ]

                # Create relationships between nearby entities (simplified)
                if len(nearby_entities) >= 2:
                    # Take first two entities for simplicity
                    subject = nearby_entities[0]
                    obj = nearby_entities[1]

                    # Avoid self-relationships
                    if subject.text != obj.text:
                        relationships.append(Relationship(
                            subject=subject.text,
                            predicate=predicate,
                            object=obj.text,
                            confidence=0.5,  # Low confidence for rule-based
                            source_text=text[max(0, match_start-30):min(len(text), match_end+30)]
                        ))

        # Deduplicate relationships
        return self._deduplicate_relationships(relationships)

    def _deduplicate_entities(self, entities: List[Entity]) -> List[Entity]:
        """Remove duplicate entities based on text and type."""
        seen = set()
        unique_entities = []
        for entity in entities:
            key = (entity.text.lower(), entity.entity_type)
            if key not in seen:
                seen.add(key)
                unique_entities.append(entity)
        return unique_entities

    def _deduplicate_relationships(self, relationships: List[Relationship]) -> List[Relationship]:
        """Remove duplicate relationships."""
        seen = set()
        unique_relationships = []
        for rel in relationships:
            key = (rel.subject.lower(), rel.predicate.lower(), rel.object.lower())
            if key not in seen:
                seen.add(key)
                unique_relationships.append(rel)
        return unique_relationships

    def _add_entity_findings(self, context: EvidenceContext, entities: List[Entity]):
        """Add entity findings to the context."""
        for i, entity in enumerate(entities):
            context.add_finding(Finding(
                key=f"entity.{entity.entity_type}",
                value={
                    "text": entity.text,
                    "entity_type": entity.entity_type,
                    "confidence": entity.confidence,
                    "source_text": entity.source_text,
                },
                confidence_level=self._score_to_confidence_level(entity.confidence),
                confidence_score=entity.confidence,
                extraction_method="entity_extraction_rule_based",
            ))

    def _add_relationship_findings(self, context: EvidenceContext, relationships: List[Relationship]):
        """Add relationship findings to the context."""
        for i, relationship in enumerate(relationships):
            context.add_finding(Finding(
                key="relationship",
                value={
                    "subject": relationship.subject,
                    "predicate": relationship.predicate,
                    "object": relationship.object,
                    "confidence": relationship.confidence,
                    "source_text": relationship.source_text,
                },
                confidence_level=self._score_to_confidence_level(relationship.confidence),
                confidence_score=relationship.confidence,
                extraction_method="entity_extraction_rule_based",
            ))

    def _score_to_confidence_level(self, score: float) -> str:
        """Convert numeric score to confidence level."""
        if score >= 0.8:
            return "high"
        elif score >= 0.5:
            return "medium"
        else:
            return "low"

    def _entity_to_dict(self, entity: Entity) -> Dict[str, Any]:
        """Convert Entity to dictionary for metadata storage."""
        return {
            "text": entity.text,
            "entity_type": entity.entity_type,
            "confidence": entity.confidence,
            "source_text": entity.source_text,
        }

    def _relationship_to_dict(self, relationship: Relationship) -> Dict[str, Any]:
        """Convert Relationship to dictionary for metadata storage."""
        return {
            "subject": relationship.subject,
            "predicate": relationship.predicate,
            "object": relationship.object,
            "confidence": relationship.confidence,
            "source_text": relationship.source_text,
        }