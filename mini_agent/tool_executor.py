from __future__ import annotations

from .tool_registry import ToolRegistry
from .types import ToolCall, ToolResult


class ToolExecutor:
    def __init__(self, registry: ToolRegistry) -> None:
        self.registry = registry

    def execute(self, tool_call: ToolCall) -> ToolResult:
        try:
            tool = self.registry.get(tool_call.name)
            output = tool.invoke(tool_call.arguments)
            return ToolResult(name=tool_call.name, ok=True, output=output)
        except Exception as exc:  # noqa: BLE001 - runtime boundary should capture all tool failures.
            return ToolResult(name=tool_call.name, ok=False, error=f"{type(exc).__name__}: {exc}")
