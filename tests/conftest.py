import pytest


@pytest.fixture(autouse=True)
def reset_env(monkeypatch):
    """Ensure tests run with predictable environment."""
    monkeypatch.setenv("GOOGLE_API_KEY", "fake-google-key")
    monkeypatch.setenv("AWS_REGION", "us-east-1")
    monkeypatch.setenv("S3_BUCKET_NAME", "test-bucket")
    monkeypatch.setenv("SQS_QUEUE_URL", "http://localhost:4566/000000000000/test-queue")
    monkeypatch.setenv("UPLOAD_SERVICE_URL", "http://localhost:8001")
    monkeypatch.setenv("REPORT_SERVICE_URL", "http://localhost:8003")
    monkeypatch.setenv("INTERNAL_SERVICE_TOKEN", "test-token")
