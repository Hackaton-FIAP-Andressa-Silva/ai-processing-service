from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    APP_NAME: str = "ai-processing-service"

    # Google Gemini
    GOOGLE_API_KEY: str

    # AWS
    AWS_REGION: str = "us-east-1"
    AWS_ENDPOINT_URL: Optional[str] = None
    S3_BUCKET_NAME: str = "architecture-diagrams"
    SQS_QUEUE_URL: str

    # Service URLs (internal Docker network)
    UPLOAD_SERVICE_URL: str = "http://upload-service:8001"
    REPORT_SERVICE_URL: str = "http://report-service:8003"

    # Internal auth
    INTERNAL_SERVICE_TOKEN: str = "internal-changeme"

    class Config:
        env_file = ".env"


settings = Settings()
