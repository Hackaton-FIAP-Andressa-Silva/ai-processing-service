import asyncio
import logging
import signal

from src.infrastructure.config import settings
from src.infrastructure.logging_config import setup_logging

setup_logging(settings.APP_NAME)
logger = logging.getLogger(__name__)


async def main() -> None:
    from src.application.use_cases.process_diagram_use_case import ProcessDiagramUseCase
    from src.infrastructure.ai.openai_analyzer import OpenAIAnalyzer
    from src.infrastructure.http.service_clients import ReportServiceClient, UploadServiceClient
    from src.infrastructure.messaging.sqs_consumer import SQSConsumer
    from src.infrastructure.pdf.pdf_converter import PdfToPngConverter
    from src.infrastructure.storage.s3_client import S3Client

    use_case = ProcessDiagramUseCase(
        storage_port=S3Client(),
        pdf_converter=PdfToPngConverter(),
        ai_analysis_port=OpenAIAnalyzer(),
        report_service_port=ReportServiceClient(),
        upload_status_port=UploadServiceClient(),
    )

    consumer = SQSConsumer(use_case)

    def handle_shutdown(signum, frame):
        consumer.stop()

    signal.signal(signal.SIGTERM, handle_shutdown)
    signal.signal(signal.SIGINT, handle_shutdown)

    logger.info("AI Processing Service starting")
    await consumer.run()
    logger.info("AI Processing Service stopped")


if __name__ == "__main__":
    asyncio.run(main())
