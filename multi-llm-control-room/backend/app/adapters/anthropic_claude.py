"""Anthropic Claude adapter"""
import time
from typing import List, Dict, Optional, AsyncIterator, Union
from datetime import datetime
from anthropic import AsyncAnthropic
from .base import ModelAdapter, ModelResponse, ResponseChunk


# Anthropic pricing (per 1M tokens)
ANTHROPIC_PRICING = {
    "claude-3-opus-20240229": {"input": 15.00, "output": 75.00},
    "claude-3-5-sonnet-20241022": {"input": 3.00, "output": 15.00},
    "claude-3-sonnet-20240229": {"input": 3.00, "output": 15.00},
    "claude-3-haiku-20240307": {"input": 0.25, "output": 1.25},
}


class AnthropicAdapter(ModelAdapter):
    """Adapter for Anthropic Claude models"""

    def __init__(self, model_id: str, config: Dict):
        super().__init__(model_id, config)
        self.api_key = config.get("api_key")
        self.model_name = config.get("model_name", "claude-3-5-sonnet-20241022")

        if not self.api_key:
            raise ValueError("Anthropic adapter requires api_key")

        self.client = AsyncAnthropic(api_key=self.api_key)

    async def send_message(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        **kwargs
    ) -> Union[ModelResponse, AsyncIterator[ResponseChunk]]:
        """Send message to Claude"""
        start_time = time.time()

        # Claude requires max_tokens to be set
        if not max_tokens:
            max_tokens = 4096

        # Extract system message if present
        system_message = None
        claude_messages = []

        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                claude_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })

        try:
            response = await self.client.messages.create(
                model=self.model_name,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_message if system_message else None,
                messages=claude_messages,
                stream=stream
            )

            if stream:
                return self._stream(response, start_time)

            latency_ms = (time.time() - start_time) * 1000

            # Extract tokens from response
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens
            cost = self.estimate_cost(input_tokens, output_tokens)

            return ModelResponse(
                content=response.content[0].text,
                model_id=self.model_id,
                tokens=input_tokens + output_tokens,
                cost=cost,
                latency_ms=latency_ms,
                timestamp=datetime.utcnow(),
                metadata={
                    "provider": "anthropic",
                    "model": self.model_name,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens
                }
            )
        except Exception as e:
            raise Exception(f"Anthropic API error: {str(e)}")

    async def _stream(self, response, start_time: float) -> AsyncIterator[ResponseChunk]:
        """Stream response from Claude"""
        try:
            async for event in response:
                if event.type == "content_block_delta":
                    if hasattr(event.delta, 'text'):
                        yield ResponseChunk(
                            content=event.delta.text,
                            done=False,
                            model_id=self.model_id
                        )
                elif event.type == "message_stop":
                    yield ResponseChunk(
                        content="",
                        done=True,
                        model_id=self.model_id
                    )
        except Exception as e:
            raise Exception(f"Anthropic streaming error: {str(e)}")

    async def health_check(self) -> bool:
        """Check Anthropic API availability"""
        try:
            await self.client.messages.create(
                model=self.model_name,
                max_tokens=1,
                messages=[{"role": "user", "content": "hi"}]
            )
            return True
        except:
            return False

    def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Estimate cost based on Anthropic pricing"""
        pricing = ANTHROPIC_PRICING.get(self.model_name, {"input": 3.0, "output": 15.0})

        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]

        return input_cost + output_cost
