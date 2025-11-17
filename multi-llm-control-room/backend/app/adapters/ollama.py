"""Ollama adapter"""
import httpx
import json
import time
from typing import List, Dict, Optional, AsyncIterator, Union
from datetime import datetime
from .base import ModelAdapter, ModelResponse, ResponseChunk


class OllamaAdapter(ModelAdapter):
    """Adapter for Ollama local models"""

    def __init__(self, model_id: str, config: Dict):
        super().__init__(model_id, config)
        self.base_url = config.get("base_url", "http://localhost:11434")
        self.model_name = config.get("model_name")
        self.client = httpx.AsyncClient(timeout=120.0)

    async def send_message(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        **kwargs
    ) -> Union[ModelResponse, AsyncIterator[ResponseChunk]]:
        """Send message to Ollama"""
        start_time = time.time()

        payload = {
            "model": self.model_name,
            "messages": messages,
            "stream": stream,
            "options": {
                "temperature": temperature,
            }
        }

        if max_tokens:
            payload["options"]["num_predict"] = max_tokens

        if stream:
            return self._stream(payload, start_time)

        try:
            response = await self.client.post(
                f"{self.base_url}/api/chat",
                json=payload
            )
            response.raise_for_status()
            data = response.json()

            latency_ms = (time.time() - start_time) * 1000

            return ModelResponse(
                content=data["message"]["content"],
                model_id=self.model_id,
                tokens=data.get("eval_count", 0) + data.get("prompt_eval_count", 0),
                cost=0.0,  # Ollama is free (local)
                latency_ms=latency_ms,
                timestamp=datetime.utcnow(),
                metadata={"provider": "ollama"}
            )
        except httpx.HTTPError as e:
            raise Exception(f"Ollama API error: {str(e)}")

    async def _stream(self, payload: Dict, start_time: float) -> AsyncIterator[ResponseChunk]:
        """Stream response from Ollama"""
        try:
            async with self.client.stream(
                "POST",
                f"{self.base_url}/api/chat",
                json=payload
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.strip():
                        chunk_data = json.loads(line)
                        content = chunk_data.get("message", {}).get("content", "")
                        done = chunk_data.get("done", False)

                        yield ResponseChunk(
                            content=content,
                            done=done,
                            model_id=self.model_id,
                            tokens=chunk_data.get("eval_count") if done else None
                        )

                        if done:
                            break
        except httpx.HTTPError as e:
            raise Exception(f"Ollama streaming error: {str(e)}")

    async def health_check(self) -> bool:
        """Check Ollama availability"""
        try:
            response = await self.client.get(f"{self.base_url}/api/tags")
            return response.status_code == 200
        except:
            return False

    def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Ollama is free (local)"""
        return 0.0

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()
