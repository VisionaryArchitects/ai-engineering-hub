"""Azure OpenAI adapter"""
import time
from typing import List, Dict, Optional, AsyncIterator, Union
from datetime import datetime
from openai import AsyncAzureOpenAI
from .base import ModelAdapter, ModelResponse, ResponseChunk


# Azure OpenAI pricing (per 1K tokens)
AZURE_PRICING = {
    "gpt-4": {"input": 0.03, "output": 0.06},
    "gpt-4-32k": {"input": 0.06, "output": 0.12},
    "gpt-4-turbo": {"input": 0.01, "output": 0.03},
    "gpt-35-turbo": {"input": 0.0005, "output": 0.0015},
    "gpt-35-turbo-16k": {"input": 0.003, "output": 0.004},
}


class AzureOpenAIAdapter(ModelAdapter):
    """Adapter for Azure OpenAI"""

    def __init__(self, model_id: str, config: Dict):
        super().__init__(model_id, config)
        self.endpoint = config.get("endpoint")
        self.api_key = config.get("api_key")
        self.api_version = config.get("api_version", "2024-02-15-preview")
        self.deployment_name = config.get("deployment_name")
        self.model_name = config.get("model_name", "gpt-4")

        if not self.endpoint or not self.api_key:
            raise ValueError("Azure OpenAI requires endpoint and api_key")

        self.client = AsyncAzureOpenAI(
            api_key=self.api_key,
            api_version=self.api_version,
            azure_endpoint=self.endpoint
        )

    async def send_message(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        **kwargs
    ) -> Union[ModelResponse, AsyncIterator[ResponseChunk]]:
        """Send message to Azure OpenAI"""
        start_time = time.time()

        try:
            response = await self.client.chat.completions.create(
                model=self.deployment_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
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
                    "provider": "azure_openai",
                    "model": self.model_name,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens
                }
            )
        except Exception as e:
            raise Exception(f"Azure OpenAI API error: {str(e)}")

    async def _stream(self, response, start_time: float) -> AsyncIterator[ResponseChunk]:
        """Stream response from Azure OpenAI"""
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
            raise Exception(f"Azure OpenAI streaming error: {str(e)}")

    async def health_check(self) -> bool:
        """Check Azure OpenAI availability"""
        try:
            # Simple test with minimal tokens
            await self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[{"role": "user", "content": "hi"}],
                max_tokens=1
            )
            return True
        except:
            return False

    def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Estimate cost based on Azure pricing"""
        pricing = AZURE_PRICING.get(self.model_name, {"input": 0.01, "output": 0.03})

        input_cost = (input_tokens / 1000) * pricing["input"]
        output_cost = (output_tokens / 1000) * pricing["output"]

        return input_cost + output_cost
