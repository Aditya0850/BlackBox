"""Pipeline orchestrator - Coordinates the execution of pipeline stages."""
import logging
from typing import Optional

from .contracts import (
    EvidenceContext,
    Finding,
    PipelineStage,
    StageExecutionRecord,
    StageStatus,
)

logger = logging.getLogger(__name__)


class PipelineOrchestrator:
    """Orchestrates the execution of pipeline stages."""

    def __init__(self, stages: list[PipelineStage], pipeline_version: str):
        self.stages = stages
        self.pipeline_version = pipeline_version
        self._stage_map = {stage.name: stage for stage in stages}

    def run(self, context: EvidenceContext) -> EvidenceContext:
        """Run all pipeline stages sequentially."""
        logger.info(f"Starting pipeline v{self.pipeline_version} for evidence {context.evidence_id}")

        for stage in self.stages:
            context = self._run_stage(stage, context)

        logger.info(f"Pipeline completed for evidence {context.evidence_id}")
        return context

    def _run_stage(self, stage: PipelineStage, context: EvidenceContext) -> EvidenceContext:
        """Run a single pipeline stage with error handling."""
        import time
        from datetime import datetime

        started_at = datetime.utcnow()
        logger.info(f"Running stage: {stage.name}")

        record = StageExecutionRecord(
            stage_name=stage.name,
            status=StageStatus.RETRYING,
            started_at=started_at,
        )

        try:
            # Run the stage
            context = stage.run(context)

            # Mark as success
            finished_at = datetime.utcnow()
            record.status = StageStatus.SUCCESS
            record.finished_at = finished_at
            record.model_version = getattr(stage, "model_version", None)

            logger.info(f"Stage {stage.name} completed successfully")

        except Exception as e:
            # Mark as failed but don't re-raise - let pipeline continue
            finished_at = datetime.utcnow()
            record.status = StageStatus.FAILED
            record.finished_at = finished_at
            record.error_details = str(e)
            record.reason = f"Stage {stage.name} failed: {type(e).__name__}"

            logger.error(f"Stage {stage.name} failed: {e}", exc_info=True)

        finally:
            context.record_execution(record)

        return context

    def get_stage(self, name: str) -> Optional[PipelineStage]:
        """Get a stage by name."""
        return self._stage_map.get(name)

    def run_single_stage(self, stage_name: str, context: EvidenceContext) -> EvidenceContext:
        """Run a single stage by name."""
        stage = self.get_stage(stage_name)
        if not stage:
            raise ValueError(f"Stage '{stage_name}' not found in pipeline")
        return self._run_stage(stage, context)