"""Base model adapter interface"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, AsyncIterator, Union, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ResponseChunk:
    """Streaming response chunk"""
    content: str
    done: bool
    model_id: str
    tokens: Optional[int] = None


@dataclass
class ModelResponse:
    """Model response"""
    content: str
    model_id: str
    tokens: Optional[int] = None
    cost: Optional[float] = None
    latency_ms: float
    timestamp: datetime
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class ModelAdapter(ABC):
    """Base adapter interface for LLM providers"""

    def __init__(self, model_id: str, config: Dict[str, Any]):
        self.model_id = model_id
        self.config = config

    @abstractmethod
    async def send_message(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        **kwargs
    ) -> Union[ModelResponse, AsyncIterator[ResponseChunk]]:
        """Send message to model and get response"""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if provider is healthy"""
        pass

    @abstractmethod
    def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Estimate cost for token usage"""
        pass

    def _format_messages(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Format messages for provider (override if needed)"""
        return messages
