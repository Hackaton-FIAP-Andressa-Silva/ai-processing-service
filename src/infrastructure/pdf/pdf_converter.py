import io
import logging

from pdf2image import convert_from_bytes
from src.application.ports.infrastructure_ports import PDFConverterPort

logger = logging.getLogger(__name__)


class PdfToPngConverter(PDFConverterPort):
    def to_image(self, pdf_content: bytes) -> bytes:
        """Convert first page of PDF to PNG bytes at 150 DPI."""
        images = convert_from_bytes(pdf_content, dpi=150, first_page=1, last_page=1)
        if not images:
            raise ValueError("PDF has no pages or could not be converted")

        buf = io.BytesIO()
        images[0].save(buf, format="PNG")
        logger.info("PDF page converted to PNG", extra={"image_size": buf.tell()})
        return buf.getvalue()
