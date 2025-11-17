"""OpenAI-compatible adapter (for LM Studio, vLLM, etc.)"""
import time
from typing import List, Dict, Optional, AsyncIterator, Union
from datetime import datetime
from openai import AsyncOpenAI
from .base import ModelAdapter, ModelResponse, ResponseChunk


class OpenAICompatibleAdapter(ModelAdapter):
    """Adapter for OpenAI-compatible APIs (LM Studio, vLLM, etc.)"""

    def __init__(self, model_id: str, config: Dict):
        super().__init__(model_id, config)
        self.base_url = config.get("base_url", "http://localhost:1234/v1")
        self.api_key = config.get("api_key", "not-needed")
        self.model_name = config.get("model_name", "local-model")

        self.client = AsyncOpenAI(
            base_url=self.base_url,
            api_key=self.api_key
        )

    async def send_message(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        **kwargs
    ) -> Union[ModelResponse, AsyncIterator[ResponseChunk]]:
        """Send message to OpenAI-compatible API"""
        start_time = time.time()

        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream
            )

            if stream:
                return self._stream(response, start_time)

            latency_ms = (time.time() - start_time) * 1000

            return ModelResponse(
                content=response.choices[0].message.content,
                model_id=self.model_id,
                tokens=response.usage.total_tokens if response.usage else None,
                cost=0.0,  # Local models are free
                latency_ms=latency_ms,
                timestamp=datetime.utcnow(),
                metadata={"provider": "openai_compatible"}
            )
        except Exception as e:
            raise Exception(f"OpenAI-compatible API error: {str(e)}")

    async def _stream(self, response, start_time: float) -> AsyncIterator[ResponseChunk]:
        """Stream response"""
        try:
            async for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    done = chunk.choices[0].finish_reason is not None

                    yield ResponseChunk(
                        content=content,
                        done=done,
                        model_id=self.model_id
                    )
        except Exception as e:
            raise Exception(f"OpenAI-compatible streaming error: {str(e)}")

    async def health_check(self) -> bool:
        """Check API availability"""
        try:
            await self.client.models.list()
            return True
        except:
            return False

    def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Local models are typically free"""
        return 0.0
