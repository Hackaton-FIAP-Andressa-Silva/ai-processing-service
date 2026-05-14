import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.application.use_cases.process_diagram_use_case import ProcessDiagramUseCase
from src.domain.entities.analysis import (
    AnalysisResult, Component, Risk, Recommendation, Severity, Priority
)


def make_analysis_result(upload_id="test-id"):
    return AnalysisResult(
        upload_id=upload_id,
        summary="Microservices architecture with API Gateway",
        components=[Component("API Gateway", "Gateway", "Entry point", "Kong")],
        risks=[Risk("SPOF", Severity.HIGH, "Single point of failure", "Downtime", ["API Gateway"])],
        recommendations=[Recommendation("Add redundancy", Priority.HIGH, "Deploy multiple instances", "HA")],
        processing_time_seconds=5.0,
        ai_model="gpt-4o",
    )


@pytest.fixture
def mock_storage():
    s = AsyncMock()
    s.download = AsyncMock(return_value=b"fake-png-bytes")
    return s


@pytest.fixture
def mock_pdf_converter():
    c = MagicMock()
    c.to_image = MagicMock(return_value=b"fake-png-bytes")
    return c


@pytest.fixture
def mock_ai():
    a = AsyncMock()
    a.analyze = AsyncMock(return_value=make_analysis_result())
    return a


@pytest.fixture
def mock_report_service():
    r = AsyncMock()
    r.create_report = AsyncMock(return_value=None)
    return r


@pytest.fixture
def mock_upload_status():
    u = AsyncMock()
    u.update_status = AsyncMock(return_value=None)
    return u


@pytest.fixture
def use_case(mock_storage, mock_pdf_converter, mock_ai, mock_report_service, mock_upload_status):
    return ProcessDiagramUseCase(
        storage_port=mock_storage,
        pdf_converter=mock_pdf_converter,
        ai_analysis_port=mock_ai,
        report_service_port=mock_report_service,
        upload_status_port=mock_upload_status,
    )


@pytest.mark.asyncio
async def test_process_png_success(use_case, mock_upload_status, mock_report_service, mock_ai):
    await use_case.execute("upload-1", "uploads/upload-1/arch.png", "arch.png", "image/png")

    # Status flow: PROCESSING → ANALYZED
    calls = [c.args[1] for c in mock_upload_status.update_status.call_args_list]
    assert calls == ["PROCESSING", "ANALYZED"]
    mock_report_service.create_report.assert_called_once()
    mock_ai.analyze.assert_called_once()


@pytest.mark.asyncio
async def test_process_pdf_success(use_case, mock_pdf_converter, mock_upload_status):
    await use_case.execute("upload-2", "uploads/upload-2/arch.pdf", "arch.pdf", "application/pdf")

    mock_pdf_converter.to_image.assert_called_once()
    calls = [c.args[1] for c in mock_upload_status.update_status.call_args_list]
    assert "ANALYZED" in calls


@pytest.mark.asyncio
async def test_process_ai_failure_sets_error_status(
    use_case, mock_ai, mock_upload_status, mock_report_service
):
    mock_ai.analyze = AsyncMock(side_effect=RuntimeError("AI service unavailable"))

    with pytest.raises(RuntimeError):
        await use_case.execute("upload-3", "uploads/upload-3/arch.png", "arch.png", "image/png")

    calls = [(c.args[1], c.args[2] if len(c.args) > 2 else c.kwargs.get("error_message"))
             for c in mock_upload_status.update_status.call_args_list]
    statuses = [c[0] for c in calls]
    assert "ERROR" in statuses
    mock_report_service.create_report.assert_not_called()
