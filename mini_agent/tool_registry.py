from __future__ import annotations

from copy import deepcopy
from typing import Any

from langchain_core.tools import BaseTool


DANGEROUS_METADATA_KEY = "dangerous"


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        if tool.name in self._tools:
            raise ValueError(f"tool already registered: {tool.name}")
        self._tools[tool.name] = tool

    def get(self, name: str) -> BaseTool:
        try:
            return self._tools[name]
        except KeyError as exc:
            raise KeyError(f"unknown tool: {name}") from exc

    def schemas(self) -> list[dict]:
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "parameters": _tool_parameters_schema(tool),
                "dangerous": self.is_dangerous(tool.name),
            }
            for tool in self.tools()
        ]

    def names(self) -> list[str]:
        return sorted(self._tools)

    def tools(self) -> list[BaseTool]:
        return [self._tools[name] for name in self.names()]

    def is_dangerous(self, name: str) -> bool:
        tool = self.get(name)
        return bool((tool.metadata or {}).get(DANGEROUS_METADATA_KEY, False))


def _tool_parameters_schema(tool: BaseTool) -> dict[str, Any]:
    args_schema = getattr(tool, "args_schema", None)
    if args_schema is not None:
        if isinstance(args_schema, dict):
            return deepcopy(args_schema)
        if hasattr(args_schema, "model_json_schema"):
            return args_schema.model_json_schema()

    return {
        "type": "object",
        "properties": deepcopy(getattr(tool, "args", {}) or {}),
    }
