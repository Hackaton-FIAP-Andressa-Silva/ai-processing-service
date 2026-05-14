from typing import List
from pydantic import BaseModel, field_validator


class ComponentSchema(BaseModel):
    name: str
    type: str
    description: str
    technology: str


class RiskSchema(BaseModel):
    title: str
    severity: str
    description: str
    impact: str
    affected_components: List[str] = []

    @field_validator("severity")
    @classmethod
    def validate_severity(cls, v: str) -> str:
        allowed = {"HIGH", "MEDIUM", "LOW"}
        if v.upper() not in allowed:
            raise ValueError(f"severity must be one of {allowed}, got '{v}'")
        return v.upper()


class RecommendationSchema(BaseModel):
    title: str
    priority: str
    description: str
    rationale: str

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v: str) -> str:
        allowed = {"HIGH", "MEDIUM", "LOW"}
        if v.upper() not in allowed:
            raise ValueError(f"priority must be one of {allowed}, got '{v}'")
        return v.upper()


class AnalysisResponseSchema(BaseModel):
    summary: str
    components: List[ComponentSchema]
    risks: List[RiskSchema]
    recommendations: List[RecommendationSchema]

    @field_validator("summary")
    @classmethod
    def validate_summary(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("summary cannot be empty")
        return v.strip()
