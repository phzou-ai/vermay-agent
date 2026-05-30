# Key Modules

## Entry Point

`mini_agent/main.py`

- Defines the `mini-agent` CLI.
- Builds the active LangGraph runtime.
- Wires model adapters, tools, trace logging, progress reporting, and approval handling.
- Handles approval resume CLI options.
- Owns terminal-only interactive approval prompting.

## LangGraph Runtime

`mini_agent/langgraph_runtime/`

- `state.py`: standard LangGraph state using `messages: Annotated[list[BaseMessage], add_messages]`.
- `nodes.py`: model, permission, approval, tool-message recording, and loop-control nodes.
- `routing.py`: message routing helpers based on `AIMessage.tool_calls`.
- `graph.py`: graph topology using `ToolNode` after permission and approval checks.
- `runner.py`: runtime wrapper around the compiled graph.
- `results.py`: structured runtime result type and API-facing result payload helpers.
- `model_adapters.py`: adapter from the project model client to a thin `AIMessage` wrapper.
- `model_factory.py`: provider factory for constructing runtime model adapters.

This package is the only active runtime path. It is the production-oriented path and uses LangChain / LangGraph standard message and tool execution types.

## Shared Harness Components

`mini_agent/`

- `context_builder.py`: builds the default system prompt and remains the source for context policy text.
- `tooling.py`: helper for creating `StructuredTool` objects with Pydantic `args_schema` and project metadata.
- `tool_registry.py`: stores `StructuredTool` objects and exposes model-facing schemas derived from each tool's `args_schema`.
- `permission.py`: blocks dangerous tools before execution.
- `result_summary.py`: shared summary helpers for terminal progress output.
- `trace.py`: writes JSONL runtime events.
- `progress.py`: renders the default human-readable harness progress transcript.
- `memory.py`: minimal file-backed memory placeholder.
- `types.py`: shared dataclasses for project message, tool-call, result, observation, and model-response payloads.

The active tool schema source is each tool's Pydantic `args_schema`. `ToolRegistry.schemas()` derives the model-facing schema from the same `StructuredTool` objects that `ToolNode` executes.

`tool_executor.py` and `observation.py` are retained for compatibility and explicit harness tests. They are not the active ToolNode execution path.

## Model Adapters

`mini_agent/model_clients/ollama.py`

- Calls Ollama `/api/chat`.
- Uses a small JSON action protocol for final answers and tool calls.
- Reads default model configuration from `.env`, `.env.local`, `.env.dev.local`, or shell environment.

`mini_agent/langgraph_runtime/model_factory.py`

- Builds provider-specific model adapters for the active runtime.
- Currently supports `ollama`.
- Future providers such as vLLM or OpenAI should be added here instead of being wired directly into `main.py`.

## Tool Domains

`mini_agent/tools/devops/`

- Local file and log inspection tools.
- Local sample Kubernetes data tools.
- SSH-backed read-only Kubernetes tools.
- Dangerous tool placeholders that require approval.

`mini_agent/tools/weather/`

- `weather_forecast` read-only external data tool backed by `wttr.in`.

## Infrastructure

`mini_agent/infra/ssh.py`

- Builds strict SSH commands from environment configuration.
- Enforces host key checking and known hosts usage.
- Redacts identity file path in returned command traces.

## Archive

`archive/hands_on_langgraph_runtime/`

- Contains the earlier explicit harness implementation.
- Is not exposed through the CLI.
- Is not part of the default pytest suite.
- Should be treated as historical reference material, not a second runtime track.
