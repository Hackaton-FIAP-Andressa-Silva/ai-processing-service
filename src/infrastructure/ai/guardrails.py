import json
import logging
import time
from typing import Any, Dict

from pydantic import ValidationError

from src.infrastructure.ai.schemas import AnalysisResponseSchema

logger = logging.getLogger(__name__)


class GuardrailViolationError(Exception):
    pass


def validate_analysis_output(raw_data: Dict[str, Any]) -> AnalysisResponseSchema:
    """
    Validate and sanitize the LLM output.
    Raises GuardrailViolationError if the output does not meet requirements.
    """
    try:
        result = AnalysisResponseSchema.model_validate(raw_data)
    except ValidationError as exc:
        logger.warning("Guardrail violation: schema validation failed", extra={"errors": exc.errors()})
        raise GuardrailViolationError(f"Output schema validation failed: {exc}") from exc

    # Sanitize strings
    result.summary = _sanitize_string(result.summary)
    for component in result.components:
        component.name = _sanitize_string(component.name)
        component.description = _sanitize_string(component.description)
    for risk in result.risks:
        risk.title = _sanitize_string(risk.title)
        risk.description = _sanitize_string(risk.description)
        risk.impact = _sanitize_string(risk.impact)
    for rec in result.recommendations:
        rec.title = _sanitize_string(rec.title)
        rec.description = _sanitize_string(rec.description)
        rec.rationale = _sanitize_string(rec.rationale)

    return result


def _sanitize_string(value: str) -> str:
    if not isinstance(value, str):
        return str(value)
    return value.strip()[:2000]  # Trim whitespace and cap length
