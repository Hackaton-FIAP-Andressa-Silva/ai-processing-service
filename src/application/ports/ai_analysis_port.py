from abc import ABC, abstractmethod
from src.domain.entities.analysis import AnalysisResult


class AIAnalysisPort(ABC):
    @abstractmethod
    async def analyze(self, image_base64: str, content_type: str) -> AnalysisResult:
        """Analyze an architecture diagram image and return structured results."""
        ...
