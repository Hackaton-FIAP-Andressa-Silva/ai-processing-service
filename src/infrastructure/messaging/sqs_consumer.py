import asyncio
import json
import logging
import uuid

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from src.application.use_cases.process_diagram_use_case import ProcessDiagramUseCase
from src.infrastructure.config import settings
from src.infrastructure.logging_config import trace_id_var

logger = logging.getLogger(__name__)

WAIT_TIME_SECONDS = 20
VISIBILITY_TIMEOUT = 300


class SQSConsumer:
    def __init__(self, use_case: ProcessDiagramUseCase) -> None:
        self._use_case = use_case
        self._running = True
        self._sqs = boto3.client(
            "sqs",
            region_name=settings.AWS_REGION,
            endpoint_url=settings.AWS_ENDPOINT_URL or None,
        )

    def stop(self) -> None:
        logger.info("Shutdown signal received, stopping consumer")
        self._running = False

    async def run(self) -> None:
        logger.info("SQS consumer started", extra={"queue_url": settings.SQS_QUEUE_URL})

        while self._running:
            try:
                response = self._sqs.receive_message(
                    QueueUrl=settings.SQS_QUEUE_URL,
                    MaxNumberOfMessages=1,
                    WaitTimeSeconds=WAIT_TIME_SECONDS,
                    VisibilityTimeout=VISIBILITY_TIMEOUT,
                )
                messages = response.get("Messages", [])

                if not messages:
                    continue

                message = messages[0]
                receipt_handle = message["ReceiptHandle"]
                body = json.loads(message["Body"])

                # Set trace_id for the duration of this message's processing
                upload_id = body.get("upload_id", str(uuid.uuid4()))
                token = trace_id_var.set(upload_id)

                logger.info(
                    "Message received from SQS",
                    extra={"upload_id": upload_id, "message_id": message["MessageId"]},
                )

                try:
                    await self._use_case.execute(
                        upload_id=body["upload_id"],
                        s3_key=body["s3_key"],
                        filename=body["filename"],
                        content_type=body["content_type"],
                    )

                    # Delete only on success
                    self._sqs.delete_message(
                        QueueUrl=settings.SQS_QUEUE_URL,
                        ReceiptHandle=receipt_handle,
                    )
                    logger.info("Message deleted from SQS", extra={"upload_id": upload_id})
                finally:
                    trace_id_var.reset(token)

            except (BotoCoreError, ClientError) as exc:
                logger.error("SQS error", extra={"error": str(exc)})
                await asyncio.sleep(5)
            except Exception as exc:
                logger.error("Error processing message", extra={"error": str(exc)}, exc_info=True)
                # Message is NOT deleted — will be retried or go to DLQ
                await asyncio.sleep(1)
