# Operations

## Install

```bash
cd <repo-root>
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
```

## Run

```bash
mini-agent "weather forecast for Shanghai"
```

The CLI uses `mini_agent/langgraph_runtime/`. No alternate runtime is exposed through the active CLI.

## Model Configuration

The runtime builds model adapters through a provider factory. The current provider is `ollama`.

Default Ollama configuration is read from `.env` and can be overridden by `.env.local`, `.env.dev.local`, shell environment variables, or CLI flags.

```bash
MINI_AGENT_OLLAMA_MODEL=deepseek-v4-flash:cloud
MINI_AGENT_OLLAMA_BASE_URL=http://127.0.0.1:11434
MINI_AGENT_OLLAMA_TIMEOUT_SECONDS=120
```

CLI override example:

```bash
mini-agent "weather forecast for Shanghai" \
  --model-provider ollama \
  --ollama-model qwen3.6:27b \
  --ollama-base-url http://127.0.0.1:11434 \
  --ollama-timeout-seconds 120
```

Future model providers should be added through `mini_agent/langgraph_runtime/model_factory.py`.

## Approval Resume

Dangerous tools require approval and pause the graph through LangGraph interrupt/resume.

In an interactive terminal, the default command prompts for approval and resumes in the same process:

```bash
mini-agent "run a dangerous operation" --thread-id approval-session
```

The active runtime currently uses an in-memory checkpointer. Cross-process manual resume is therefore not durable yet. A durable checkpointer should be added before relying on resume across separate CLI processes, server workers, or restarts.

Interactive approval asks at most once per run by default. If the model requests another dangerous tool after approval, the run stops instead of repeatedly prompting.

Detailed interrupt, checkpoint, and resume mechanics are documented in [langgraph-interrupt-resume.md](langgraph-interrupt-resume.md).

## Terminal Progress

`ProgressReporter` is enabled by default and writes a compact harness transcript to stderr. It should stay concise and describe harness-level behavior:

```text
loop 1
  context ...
  model_call ...
  model_decision ...
```

The terminal transcript is for scanability. It is not the durable audit log and should not try to expose full tool payloads.

Disable progress output:

```bash
mini-agent "weather forecast for Shanghai" --no-progress
```

## JSONL Traces

Machine-readable traces are written to:

```text
traces/*.jsonl
```

`TraceLogger` is the durable audit log. It can store fuller payloads than terminal output, including tool messages, observations, permission decisions, and raw model responses.

## Tests

```bash
.venv/bin/python -m pytest
```
