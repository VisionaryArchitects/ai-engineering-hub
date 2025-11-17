"""Adapter factory for creating model adapters"""
from typing import Dict, Type
from .base import ModelAdapter
from .ollama import OllamaAdapter
from .openai_compatible import OpenAICompatibleAdapter
from .azure_openai import AzureOpenAIAdapter


class AdapterFactory:
    """Factory for creating model adapters"""

    _adapters: Dict[str, Type[ModelAdapter]] = {
        "ollama": OllamaAdapter,
        "openai_compatible": OpenAICompatibleAdapter,
        "lmstudio": OpenAICompatibleAdapter,  # LM Studio uses OpenAI format
        "azure_openai": AzureOpenAIAdapter,
    }

    @classmethod
    def register(cls, provider_type: str, adapter_class: Type[ModelAdapter]):
        """Register a new adapter type"""
        cls._adapters[provider_type] = adapter_class

    @classmethod
    def create(cls, model_id: str, provider_type: str, config: Dict) -> ModelAdapter:
        """Create an adapter instance"""
        adapter_class = cls._adapters.get(provider_type)

        if not adapter_class:
            raise ValueError(f"Unknown provider type: {provider_type}")

        return adapter_class(model_id, config)

    @classmethod
    def get_supported_providers(cls) -> list:
        """Get list of supported providers"""
        return list(cls._adapters.keys())
