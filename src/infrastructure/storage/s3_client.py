import logging

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from src.application.ports.infrastructure_ports import StoragePort
from src.infrastructure.config import settings

logger = logging.getLogger(__name__)


class S3Client(StoragePort):
    def __init__(self) -> None:
        self._client = boto3.client(
            "s3",
            region_name=settings.AWS_REGION,
            endpoint_url=settings.AWS_ENDPOINT_URL or None,
        )

    async def download(self, key: str) -> bytes:
        try:
            response = self._client.get_object(Bucket=settings.S3_BUCKET_NAME, Key=key)
            content = response["Body"].read()
            logger.info("File downloaded from S3", extra={"s3_key": key, "size": len(content)})
            return content
        except (BotoCoreError, ClientError) as exc:
            logger.error("S3 download failed", extra={"s3_key": key, "error": str(exc)})
            raise
