from dataclasses import dataclass, field
from enum import Enum
from typing import List


class Severity(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class Priority(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


@dataclass
class Component:
    name: str
    type: str
    description: str
    technology: str


@dataclass
class Risk:
    title: str
    severity: Severity
    description: str
    impact: str
    affected_components: List[str] = field(default_factory=list)


@dataclass
class Recommendation:
    title: str
    priority: Priority
    description: str
    rationale: str


@dataclass
class AnalysisResult:
    upload_id: str
    summary: str
    components: List[Component]
    risks: List[Risk]
    recommendations: List[Recommendation]
    processing_time_seconds: float
    ai_model: str = "gpt-4o"
