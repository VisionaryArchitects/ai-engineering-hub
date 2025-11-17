"""Pydantic schemas for API request/response"""
from datetime import datetime
from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field


# ============================================================================
# Message Schemas
# ============================================================================

class Message(BaseModel):
    """Chat message"""
    id: str
    role: Literal["user", "assistant", "system", "tool"]
    content: str
    model_id: Optional[str] = None
    timestamp: datetime
    tokens: Optional[int] = None
    cost: Optional[float] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class MessageCreate(BaseModel):
    """Create new message"""
    role: Literal["user", "assistant", "system"]
    content: str


# ============================================================================
# Model Configuration Schemas
# ============================================================================

class ModelConfig(BaseModel):
    """Model configuration"""
    id: str
    provider: str  # ollama, openai, azure_openai, nvidia, etc.
    model_name: str
    role: Optional[str] = None
    system_prompt: Optional[str] = None
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    top_p: Optional[float] = None
    stop_sequences: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ModelConfigCreate(BaseModel):
    """Create model configuration"""
    provider: str
    model_name: str
    role: Optional[str] = None
    system_prompt: Optional[str] = None
    temperature: float = 0.7
    max_tokens: Optional[int] = None


# ============================================================================
# Session Schemas
# ============================================================================

class SessionConfig(BaseModel):
    """Session configuration"""
    routing_pattern: Literal["broadcast", "coordinator", "round_robin", "voting"] = "broadcast"
    models: List[ModelConfigCreate]
    coordinator_model_id: Optional[str] = None
    framework_config: Optional[Dict[str, Any]] = None
    mcp_servers: List[str] = Field(default_factory=list)
    cost_limit: Optional[float] = None
    tags: List[str] = Field(default_factory=list)


class Session(BaseModel):
    """Session details"""
    id: str
    conversation_id: str
    routing_pattern: str
    models: List[ModelConfig]
    coordinator_model_id: Optional[str] = None
    created_at: datetime
    status: Literal["active", "paused", "completed"]
    total_tokens: int = 0
    total_cost: float = 0.0
    message_count: int = 0


class SessionCreate(BaseModel):
    """Create new session"""
    title: Optional[str] = None
    config: SessionConfig


# ============================================================================
# Conversation Schemas
# ============================================================================

class Conversation(BaseModel):
    """Conversation details"""
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    total_tokens: int
    total_cost: float
    tags: List[str] = Field(default_factory=list)


# ============================================================================
# Response Schemas
# ============================================================================

class ModelResponse(BaseModel):
    """Model response"""
    model_id: str
    content: str
    tokens: Optional[int] = None
    cost: Optional[float] = None
    latency_ms: float
    timestamp: datetime


class MultiModelResponse(BaseModel):
    """Response from multiple models"""
    session_id: str
    responses: List[ModelResponse]
    total_tokens: int
    total_cost: float


# ============================================================================
# Export Schemas
# ============================================================================

class ExportFormat(str):
    """Export format options"""
    JSON = "json"
    MARKDOWN = "markdown"
    HTML = "html"
    PDF = "pdf"


class ExportRequest(BaseModel):
    """Export request"""
    format: Literal["json", "markdown", "html", "pdf"]
    include_metadata: bool = True
    include_costs: bool = True


# ============================================================================
# Cost Tracking Schemas
# ============================================================================

class CostEntry(BaseModel):
    """Cost tracking entry"""
    session_id: str
    model_id: str
    provider: str
    model_name: str
    input_tokens: int
    output_tokens: int
    cost: float
    timestamp: datetime


class CostSummary(BaseModel):
    """Cost summary"""
    total_cost: float
    by_provider: Dict[str, float]
    by_model: Dict[str, float]
    total_tokens: int


# ============================================================================
# Health & Status Schemas
# ============================================================================

class ModelHealth(BaseModel):
    """Model provider health status"""
    provider: str
    status: Literal["healthy", "degraded", "down"]
    latency_ms: Optional[float] = None
    last_check: datetime


class SystemHealth(BaseModel):
    """System health"""
    status: Literal["healthy", "degraded", "down"]
    models: List[ModelHealth]
    database: bool
    redis: bool
