from __future__ import annotations

import argparse
from pathlib import Path

from .context_builder import ContextBuilder
from .memory import MemoryStore
from .models import OllamaModelClient
from .observation import ObservationHandler
from .permission import PermissionGate
from .runtime import MiniAgentRuntime
from .tool_executor import ToolExecutor
from .tool_registry import ToolRegistry
from .tools.devops import register_devops_tools
from .trace import TraceLogger


ROOT = Path(__file__).resolve().parents[1]


def build_runtime(
    trace_name: str = "latest.jsonl",
    ollama_model: str = "deepseek-v4-flash:cloud",
    ollama_base_url: str = "http://127.0.0.1:11434",
) -> MiniAgentRuntime:
    registry = ToolRegistry()
    register_devops_tools(registry)

    return MiniAgentRuntime(
        model=OllamaModelClient(model=ollama_model, base_url=ollama_base_url),
        registry=registry,
        context_builder=ContextBuilder(),
        permission_gate=PermissionGate(registry),
        tool_executor=ToolExecutor(registry),
        observation_handler=ObservationHandler(),
        memory=MemoryStore(ROOT / "data" / "memory.txt"),
        trace=TraceLogger(ROOT / "traces" / trace_name),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Mini Agent Workbench")
    parser.add_argument("prompt", nargs="*", help="User input")
    parser.add_argument("--trace", default="latest.jsonl", help="Trace JSONL filename")
    parser.add_argument("--ollama-model", default="deepseek-v4-flash:cloud")
    parser.add_argument("--ollama-base-url", default="http://127.0.0.1:11434")
    args = parser.parse_args()

    user_input = " ".join(args.prompt).strip() or "check cluster status"
    runtime = build_runtime(
        trace_name=args.trace,
        ollama_model=args.ollama_model,
        ollama_base_url=args.ollama_base_url,
    )
    print(runtime.run(user_input))


if __name__ == "__main__":
    main()
