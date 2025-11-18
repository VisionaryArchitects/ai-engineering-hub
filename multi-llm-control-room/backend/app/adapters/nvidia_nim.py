"""NVIDIA NIM adapter for optimized LLM inference"""
import time
from typing import List, Dict, Optional, AsyncIterator, Union
from datetime import datetime
from openai import AsyncOpenAI
from .base import ModelAdapter, ModelResponse, ResponseChunk


# NVIDIA NIM pricing (approximate, per 1M tokens)
NVIDIA_PRICING = {
    "meta/llama-3.1-405b-instruct": {"input": 5.00, "output": 5.00},
    "meta/llama-3.1-70b-instruct": {"input": 0.88, "output": 0.88},
    "meta/llama-3.1-8b-instruct": {"input": 0.20, "output": 0.20},
    "mistralai/mixtral-8x7b-instruct-v0.1": {"input": 0.54, "output": 0.54},
    "microsoft/phi-3-medium-128k-instruct": {"input": 0.35, "output": 0.35},
}


class NVIDIANIMAdapter(ModelAdapter):
    """Adapter for NVIDIA NIM optimized models"""

    def __init__(self, model_id: str, config: Dict):
        super().__init__(model_id, config)
        self.api_key = config.get("api_key")
        self.model_name = config.get("model_name", "meta/llama-3.1-70b-instruct")
        self.base_url = config.get("base_url", "https://integrate.api.nvidia.com/v1")

        if not self.api_key:
            raise ValueError("NVIDIA NIM adapter requires api_key")

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
        """Send message to NVIDIA NIM"""
        start_time = time.time()

        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens or 1024,
                stream=stream
            )

            if stream:
                return self._stream(response, start_time)

            latency_ms = (time.time() - start_time) * 1000

            input_tokens = response.usage.prompt_tokens if response.usage else 0
            output_tokens = response.usage.completion_tokens if response.usage else 0
            cost = self.estimate_cost(input_tokens, output_tokens)

            return ModelResponse(
                content=response.choices[0].message.content,
                model_id=self.model_id,
                tokens=response.usage.total_tokens if response.usage else None,
                cost=cost,
                latency_ms=latency_ms,
                timestamp=datetime.utcnow(),
                metadata={
                    "provider": "nvidia_nim",
                    "model": self.model_name,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens
                }
            )
        except Exception as e:
            raise Exception(f"NVIDIA NIM API error: {str(e)}")

    async def _stream(self, response, start_time: float) -> AsyncIterator[ResponseChunk]:
        """Stream response from NVIDIA NIM"""
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
            raise Exception(f"NVIDIA NIM streaming error: {str(e)}")

    async def health_check(self) -> bool:
        """Check NVIDIA NIM API availability"""
        try:
            await self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": "hi"}],
                max_tokens=1
            )
            return True
        except:
            return False

    def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Estimate cost based on NVIDIA NIM pricing"""
        pricing = NVIDIA_PRICING.get(self.model_name, {"input": 1.0, "output": 1.0})

        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]

        return input_cost + output_cost
