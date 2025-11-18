"""HuggingFace Inference API adapter"""
import httpx
import time
from typing import List, Dict, Optional, AsyncIterator, Union
from datetime import datetime
from .base import ModelAdapter, ModelResponse, ResponseChunk


class HuggingFaceAdapter(ModelAdapter):
    """Adapter for HuggingFace Inference API"""

    def __init__(self, model_id: str, config: Dict):
        super().__init__(model_id, config)
        self.api_key = config.get("api_key")
        self.model_name = config.get("model_name")
        self.base_url = config.get("base_url", "https://api-inference.huggingface.co/models")

        if not self.api_key:
            raise ValueError("HuggingFace adapter requires api_key")

        if not self.model_name:
            raise ValueError("HuggingFace adapter requires model_name")

        self.client = httpx.AsyncClient(timeout=120.0)

    async def send_message(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        **kwargs
    ) -> Union[ModelResponse, AsyncIterator[ResponseChunk]]:
        """Send message to HuggingFace Inference API"""
        start_time = time.time()

        # Format messages as prompt (TGI-style)
        prompt = self._format_prompt(messages)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "inputs": prompt,
            "parameters": {
                "temperature": temperature,
                "max_new_tokens": max_tokens or 1024,
                "return_full_text": False,
                "do_sample": temperature > 0
            }
        }

        if stream:
            payload["stream"] = True

        try:
            if stream:
                return self._stream(headers, payload, start_time)

            response = await self.client.post(
                f"{self.base_url}/{self.model_name}",
                headers=headers,
                json=payload
            )
            response.raise_for_status()

            latency_ms = (time.time() - start_time) * 1000

            data = response.json()

            # Handle different response formats
            if isinstance(data, list):
                content = data[0].get("generated_text", "")
            else:
                content = data.get("generated_text", "")

            # HuggingFace Inference API doesn't return token counts
            # Estimate based on text length
            estimated_tokens = len(content.split()) * 1.3  # Rough estimate

            return ModelResponse(
                content=content,
                model_id=self.model_id,
                tokens=int(estimated_tokens),
                cost=0.0,  # HuggingFace Inference API has various pricing models
                latency_ms=latency_ms,
                timestamp=datetime.utcnow(),
                metadata={
                    "provider": "huggingface",
                    "model": self.model_name
                }
            )
        except httpx.HTTPError as e:
            raise Exception(f"HuggingFace API error: {str(e)}")

    async def _stream(self, headers: Dict, payload: Dict, start_time: float) -> AsyncIterator[ResponseChunk]:
        """Stream response from HuggingFace"""
        try:
            async with self.client.stream(
                "POST",
                f"{self.base_url}/{self.model_name}",
                headers=headers,
                json=payload
            ) as response:
                response.raise_for_status()

                async for line in response.aiter_lines():
                    if line.startswith("data:"):
                        data_str = line[5:].strip()
                        if data_str and data_str != "[DONE]":
                            try:
                                import json
                                chunk_data = json.loads(data_str)
                                content = chunk_data.get("token", {}).get("text", "")

                                if content:
                                    yield ResponseChunk(
                                        content=content,
                                        done=False,
                                        model_id=self.model_id
                                    )
                            except json.JSONDecodeError:
                                continue

                yield ResponseChunk(
                    content="",
                    done=True,
                    model_id=self.model_id
                )
        except httpx.HTTPError as e:
            raise Exception(f"HuggingFace streaming error: {str(e)}")

    async def health_check(self) -> bool:
        """Check HuggingFace API availability"""
        try:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            response = await self.client.get(
                f"{self.base_url}/{self.model_name}",
                headers=headers
            )
            return response.status_code == 200
        except:
            return False

    def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """HuggingFace Inference API pricing varies by model"""
        # Most models are free for inference, pro accounts have different pricing
        return 0.0

    def _format_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Format messages as a single prompt string"""
        # Simple chat format
        prompt_parts = []

        for msg in messages:
            role = msg["role"]
            content = msg["content"]

            if role == "system":
                prompt_parts.append(f"System: {content}")
            elif role == "user":
                prompt_parts.append(f"User: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")

        prompt_parts.append("Assistant:")
        return "\n\n".join(prompt_parts)

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()
