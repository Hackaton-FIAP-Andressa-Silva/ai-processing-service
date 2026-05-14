import pytest
from src.infrastructure.ai.guardrails import validate_analysis_output, GuardrailViolationError


VALID_OUTPUT = {
    "summary": "Microservices architecture with API Gateway and databases",
    "components": [
        {"name": "API Gateway", "type": "Gateway", "description": "Entry point", "technology": "Kong"}
    ],
    "risks": [
        {
            "title": "Single point of failure",
            "severity": "HIGH",
            "description": "API Gateway is a SPOF",
            "impact": "Complete system outage",
            "affected_components": ["API Gateway"],
        }
    ],
    "recommendations": [
        {
            "title": "Add redundancy",
            "priority": "HIGH",
            "description": "Deploy multiple gateway instances",
            "rationale": "Improves availability",
        }
    ],
}


def test_valid_output_passes():
    result = validate_analysis_output(VALID_OUTPUT)
    assert result.summary == VALID_OUTPUT["summary"]
    assert len(result.components) == 1
    assert len(result.risks) == 1
    assert result.risks[0].severity == "HIGH"


def test_missing_summary_fails():
    data = {**VALID_OUTPUT, "summary": ""}
    with pytest.raises(GuardrailViolationError):
        validate_analysis_output(data)


def test_missing_components_field_fails():
    data = {k: v for k, v in VALID_OUTPUT.items() if k != "components"}
    with pytest.raises(GuardrailViolationError):
        validate_analysis_output(data)


def test_invalid_severity_fails():
    data = {
        **VALID_OUTPUT,
        "risks": [
            {**VALID_OUTPUT["risks"][0], "severity": "CRITICAL"}
        ]
    }
    with pytest.raises(GuardrailViolationError):
        validate_analysis_output(data)


def test_invalid_priority_fails():
    data = {
        **VALID_OUTPUT,
        "recommendations": [
            {**VALID_OUTPUT["recommendations"][0], "priority": "URGENT"}
        ]
    }
    with pytest.raises(GuardrailViolationError):
        validate_analysis_output(data)


def test_string_sanitization():
    data = {
        **VALID_OUTPUT,
        "summary": "  Summary with extra spaces  ",
    }
    result = validate_analysis_output(data)
    assert result.summary == "Summary with extra spaces"
