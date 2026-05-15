from src.domain.entities.analysis import (
    AnalysisResult,
    Component,
    Risk,
    Recommendation,
    Severity,
    Priority,
)


def test_component_creation():
    comp = Component("API GW", "Gateway", "Entry point", "Kong")
    assert comp.name == "API GW"
    assert comp.type == "Gateway"
    assert comp.description == "Entry point"
    assert comp.technology == "Kong"


def test_risk_default_affected_components():
    risk = Risk("SPOF", Severity.HIGH, "Single point of failure", "Outage")
    assert risk.affected_components == []
    assert risk.title == "SPOF"
    assert risk.severity == Severity.HIGH
    assert risk.description == "Single point of failure"
    assert risk.impact == "Outage"


def test_risk_with_affected_components():
    risk = Risk("SPOF", Severity.HIGH, "desc", "impact", ["API GW", "DB"])
    assert len(risk.affected_components) == 2
    assert "API GW" in risk.affected_components
    assert "DB" in risk.affected_components


def test_recommendation_creation():
    rec = Recommendation("Add HA", Priority.HIGH, "Deploy multiple instances", "Improves availability")
    assert rec.title == "Add HA"
    assert rec.priority == Priority.HIGH
    assert rec.description == "Deploy multiple instances"
    assert rec.rationale == "Improves availability"


def test_severity_enum_values():
    assert Severity.HIGH == "HIGH"
    assert Severity.MEDIUM == "MEDIUM"
    assert Severity.LOW == "LOW"


def test_priority_enum_values():
    assert Priority.HIGH == "HIGH"
    assert Priority.MEDIUM == "MEDIUM"
    assert Priority.LOW == "LOW"


def test_analysis_result_creation():
    result = AnalysisResult(
        upload_id="upload-1",
        summary="Test architecture",
        components=[Component("DB", "Database", "stores data", "PostgreSQL")],
        risks=[Risk("SPOF", Severity.HIGH, "desc", "impact")],
        recommendations=[Recommendation("Add HA", Priority.MEDIUM, "desc", "rationale")],
        processing_time_seconds=3.5,
        ai_model="gemini-2.0-flash",
    )
    assert result.upload_id == "upload-1"
    assert result.summary == "Test architecture"
    assert len(result.components) == 1
    assert len(result.risks) == 1
    assert len(result.recommendations) == 1
    assert result.processing_time_seconds == 3.5
    assert result.ai_model == "gemini-2.0-flash"


def test_analysis_result_default_model():
    result = AnalysisResult(
        upload_id="upload-1",
        summary="Test",
        components=[],
        risks=[],
        recommendations=[],
        processing_time_seconds=1.0,
    )
    assert result.ai_model == "gpt-4o"


def test_analysis_result_upload_id_mutation():
    result = AnalysisResult(
        upload_id="old-id",
        summary="Test",
        components=[],
        risks=[],
        recommendations=[],
        processing_time_seconds=1.0,
    )
    result.upload_id = "new-id"
    assert result.upload_id == "new-id"


def test_severity_str_enum():
    assert Severity.HIGH.value == "HIGH"
    assert Severity("HIGH") == Severity.HIGH
    assert Severity("MEDIUM") == Severity.MEDIUM
    assert Severity("LOW") == Severity.LOW


def test_priority_str_enum():
    assert Priority.HIGH.value == "HIGH"
    assert Priority("HIGH") == Priority.HIGH
    assert Priority("LOW") == Priority.LOW
