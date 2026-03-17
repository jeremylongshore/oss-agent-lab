"""Pydantic models for inter-agent communication in OSS Agent Lab."""

from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


class Query(BaseModel):
    """A user query entering the agent pipeline."""

    user_input: str
    session_id: Optional[str] = None
    context: Optional[dict] = None


class Intent(BaseModel):
    """Parsed intent from a user query."""

    action: str
    domain: str
    confidence: float = Field(ge=0.0, le=1.0)
    parameters: dict = Field(default_factory=dict)


class SpecialistRequest(BaseModel):
    """Request routed to a specific specialist."""

    intent: Intent
    query: Query
    specialist_name: str
    tools_requested: Optional[list[str]] = None


class SpecialistResponse(BaseModel):
    """Response returned by a specialist after execution."""

    specialist_name: str
    status: Literal["success", "error", "partial"]
    result: Any
    metadata: Optional[dict] = None
    duration_ms: Optional[float] = None


class SessionContext(BaseModel):
    """Session state for multi-turn conversations."""

    session_id: str
    history: list[dict] = Field(default_factory=list)
    memory: Optional[dict] = None
