
from typing import Literal
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    session_id: str | None = None


class IntentProfile(BaseModel):
    category: Literal[
        "support", "financial", "technical",
        "general", "other"
    ]
    confidence: float = Field(ge=0, le=1)


class RiskProfile(BaseModel):
    level: Literal["low", "medium", "high"]
    reason: str


class PriorityProfile(BaseModel):
    level: Literal["low", "medium", "high", "critical"]
    score: int = Field(ge=1, le=10)


class TokenMetadata(BaseModel):
    input_tokens: int = Field(ge=0)
    output_tokens: int = Field(ge=0)
    total_tokens: int = Field(ge=0)


class FirewallResult(BaseModel):
    intent: IntentProfile
    risk: RiskProfile
    priority: PriorityProfile
    tokens: TokenMetadata


class ChatResponse(BaseModel):
    session_id: str
    response: str
    firewall: FirewallResult
