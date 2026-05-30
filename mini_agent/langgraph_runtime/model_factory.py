from __future__ import annotations

from dataclasses import dataclass

from mini_agent.model_clients import OllamaModelClient

from .model_adapters import OllamaModelAdapter
from .nodes import ModelClient


@dataclass(frozen=True)
class ModelConfig:
    provider: str = "ollama"
    ollama_model: str | None = None
    ollama_base_url: str | None = None
    ollama_timeout_seconds: int | None = None


def build_model_client(config: ModelConfig, tool_schemas: list[dict]) -> ModelClient:
    if config.provider == "ollama":
        return OllamaModelAdapter(
            client=OllamaModelClient(
                model=config.ollama_model,
                base_url=config.ollama_base_url,
                timeout_seconds=config.ollama_timeout_seconds,
            ),
            tool_schemas=tool_schemas,
        )

    raise ValueError(f"unsupported model provider: {config.provider}")
