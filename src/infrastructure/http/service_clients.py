import logging
from typing import Any, Dict

import httpx

from src.application.ports.infrastructure_ports import ReportServicePort, UploadStatusPort
from src.infrastructure.config import settings

logger = logging.getLogger(__name__)

TIMEOUT = 30.0
MAX_RETRIES = 2


class ReportServiceClient(ReportServicePort):
    async def create_report(self, upload_id: str, result: Dict[str, Any]) -> None:
        url = f"{settings.REPORT_SERVICE_URL}/api/v1/reports"
        for attempt in range(1, MAX_RETRIES + 2):
            try:
                async with httpx.AsyncClient(timeout=TIMEOUT) as client:
                    response = await client.post(
                        url,
                        json=result,
                        headers={"X-Internal-Token": settings.INTERNAL_SERVICE_TOKEN},
                    )
                    response.raise_for_status()
                    logger.info("Report created via report-service", extra={"upload_id": upload_id})
                    return
            except httpx.HTTPError as exc:
                logger.warning(
                    "Report service call failed",
                    extra={"attempt": attempt, "upload_id": upload_id, "error": str(exc)},
                )
                if attempt > MAX_RETRIES:
                    raise


class UploadServiceClient(UploadStatusPort):
    async def update_status(
        self, upload_id: str, status: str, error_message: str | None = None
    ) -> None:
        url = f"{settings.UPLOAD_SERVICE_URL}/api/v1/uploads/{upload_id}/status"
        payload = {"status": status}
        if error_message:
            payload["error_message"] = error_message

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.patch(
                    url,
                    json=payload,
                    headers={"X-Internal-Token": settings.INTERNAL_SERVICE_TOKEN},
                )
                response.raise_for_status()
                logger.info(
                    "Upload status updated",
                    extra={"upload_id": upload_id, "status": status},
                )
        except httpx.HTTPError as exc:
            # Log but don't fail — status update is best-effort
            logger.error(
                "Failed to update upload status",
                extra={"upload_id": upload_id, "status": status, "error": str(exc)},
            )
