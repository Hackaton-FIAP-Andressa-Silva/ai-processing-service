import json
import logging
import time

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

from src.application.ports.ai_analysis_port import AIAnalysisPort
from src.domain.entities.analysis import (
    AnalysisResult,
    Component,
    Risk,
    Recommendation,
    Severity,
    Priority,
)
from src.infrastructure.ai.guardrails import validate_analysis_output, GuardrailViolationError
from src.infrastructure.ai.prompt_templates import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE
from src.infrastructure.config import settings

logger = logging.getLogger(__name__)

MAX_RETRIES = 2


class OpenAIAnalyzer(AIAnalysisPort):
    def __init__(self) -> None:
        self._llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash-lite",
            temperature=0.1,
            max_output_tokens=4096,
            request_timeout=30,  # 30 s hard limit — prevents resource exhaustion
            generation_config={"response_mime_type": "application/json"},
            google_api_key=settings.GOOGLE_API_KEY,
            max_retries=1,  # disable LangChain's internal tenacity retries (app loop handles it)
        )

    async def analyze(self, image_base64: str, content_type: str) -> AnalysisResult:
        start_time = time.time()
        last_error = None

        for attempt in range(1, MAX_RETRIES + 2):
            try:
                raw = await self._call_llm(image_base64, content_type)
                validated = validate_analysis_output(raw)
                processing_time = time.time() - start_time

                return AnalysisResult(
                    upload_id="",  # Set by caller
                    summary=validated.summary,
                    components=[
                        Component(
                            name=c.name,
                            type=c.type,
                            description=c.description,
                            technology=c.technology,
                        )
                        for c in validated.components
                    ],
                    risks=[
                        Risk(
                            title=r.title,
                            severity=Severity(r.severity),
                            description=r.description,
                            impact=r.impact,
                            affected_components=r.affected_components,
                        )
                        for r in validated.risks
                    ],
                    recommendations=[
                        Recommendation(
                            title=rec.title,
                            priority=Priority(rec.priority),
                            description=rec.description,
                            rationale=rec.rationale,
                        )
                        for rec in validated.recommendations
                    ],
                    processing_time_seconds=round(processing_time, 2),
                    ai_model="gemini-2.5-flash-lite",
                )
            except (GuardrailViolationError, json.JSONDecodeError, Exception) as exc:
                last_error = exc
                logger.warning(
                    "AI analysis attempt failed",
                    extra={"attempt": attempt, "error": str(exc)},
                )
                if attempt > MAX_RETRIES:
                    break

        raise RuntimeError(f"AI analysis failed after {MAX_RETRIES + 1} attempts: {last_error}") from last_error

    async def _call_llm(self, image_base64: str, content_type: str) -> dict:
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(
                content=[
                    {"type": "text", "text": USER_PROMPT_TEMPLATE},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{content_type};base64,{image_base64}",
                        },
                    },
                ]
            ),
        ]
        response = await self._llm.ainvoke(messages)
        content = response.content
        if not content or not content.strip():
            raise ValueError("Empty response from AI model")
        # Strip markdown code fences if present (e.g. ```json ... ```)
        stripped = content.strip()
        if stripped.startswith("```"):
            stripped = stripped.split("\n", 1)[-1]
            stripped = stripped.rsplit("```", 1)[0]
        return json.loads(stripped)
