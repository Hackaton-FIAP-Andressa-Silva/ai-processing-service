from abc import ABC, abstractmethod


class StoragePort(ABC):
    @abstractmethod
    async def download(self, key: str) -> bytes:
        """Download a file from storage and return its contents."""
        ...


class PDFConverterPort(ABC):
    @abstractmethod
    def to_image(self, pdf_content: bytes) -> bytes:
        """Convert the first page of a PDF to PNG bytes."""
        ...


class ReportServicePort(ABC):
    @abstractmethod
    async def create_report(self, upload_id: str, result: dict) -> None:
        """Send the analysis result to the report service."""
        ...


class UploadStatusPort(ABC):
    @abstractmethod
    async def update_status(
        self,
        upload_id: str,
        status: str,
        error_message: str | None = None,
    ) -> None:
        """Update the processing status in the upload service."""
        ...
