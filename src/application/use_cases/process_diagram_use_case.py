import base64
import logging
import time
from dataclasses import asdict

from src.application.ports.ai_analysis_port import AIAnalysisPort
from src.application.ports.infrastructure_ports import (
    PDFConverterPort,
    ReportServicePort,
    StoragePort,
    UploadStatusPort,
)

logger = logging.getLogger(__name__)

PDF_CONTENT_TYPE = "application/pdf"


class ProcessDiagramUseCase:
    def __init__(
        self,
        storage_port: StoragePort,
        pdf_converter: PDFConverterPort,
        ai_analysis_port: AIAnalysisPort,
        report_service_port: ReportServicePort,
        upload_status_port: UploadStatusPort,
    ) -> None:
        self._storage = storage_port
        self._pdf_converter = pdf_converter
        self._ai = ai_analysis_port
        self._report_service = report_service_port
        self._upload_status = upload_status_port

    async def execute(self, upload_id: str, s3_key: str, filename: str, content_type: str) -> None:
        logger.info(
            "Starting diagram processing",
            extra={"upload_id": upload_id, "s3_key": s3_key, "content_type": content_type},
        )

        # Mark as PROCESSING
        await self._upload_status.update_status(upload_id, "PROCESSING")

        try:
            # Download file from S3
            file_content = await self._storage.download(s3_key)
            logger.info("File downloaded from S3", extra={"upload_id": upload_id, "size": len(file_content)})

            # Convert PDF to image if needed
            if content_type == PDF_CONTENT_TYPE:
                logger.info("Converting PDF to image", extra={"upload_id": upload_id})
                image_content = self._pdf_converter.to_image(file_content)
                image_content_type = "image/png"
            else:
                image_content = file_content
                image_content_type = content_type

            # Encode to base64
            image_base64 = base64.b64encode(image_content).decode("utf-8")

            # Run AI analysis
            logger.info("Starting AI analysis", extra={"upload_id": upload_id})
            result = await self._ai.analyze(image_base64, image_content_type)
            result.upload_id = upload_id
            logger.info(
                "AI analysis completed",
                extra={
                    "upload_id": upload_id,
                    "components": len(result.components),
                    "risks": len(result.risks),
                    "processing_time": result.processing_time_seconds,
                },
            )

            # Send to Report Service
            report_payload = {
                "upload_id": upload_id,
                "summary": result.summary,
                "components": [asdict(c) for c in result.components],
                "risks": [
                    {**asdict(r), "severity": r.severity.value} for r in result.risks
                ],
                "recommendations": [
                    {**asdict(rec), "priority": rec.priority.value}
                    for rec in result.recommendations
                ],
                "processing_time_seconds": result.processing_time_seconds,
                "ai_model": result.ai_model,
            }
            await self._report_service.create_report(upload_id, report_payload)
            logger.info("Report sent to report-service", extra={"upload_id": upload_id})

            # Mark as ANALYZED
            await self._upload_status.update_status(upload_id, "ANALYZED")
            logger.info("Processing completed successfully", extra={"upload_id": upload_id})

        except Exception as exc:
            logger.error(
                "Diagram processing failed",
                extra={"upload_id": upload_id, "error": str(exc)},
                exc_info=True,
            )
            await self._upload_status.update_status(
                upload_id, "ERROR", error_message=f"Processing failed: {type(exc).__name__}"
            )
            raise
