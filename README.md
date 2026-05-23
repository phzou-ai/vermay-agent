# Mini Agent Workbench

本项目用于学习 Agent Harness 的底层机制。

当前实现为 Phase 1：手写 mini runtime，不依赖 LangGraph。目标是显式展示 Agent runtime 中的核心组件：

- Context builder
- Tool registry
- Tool executor
- Observation handler
- Permission gate
- Trace logger
- Error recovery
- Minimal model client

Demo 主题：DevOps Assistant。

## 运行方式

```bash
cd /Users/phzou/Documents/Code/AI/agent
python3 -m mini_agent.main "check cluster status"
```

更多示例：

```bash
python3 -m mini_agent.main "show pod status"
python3 -m mini_agent.main "grep nginx errors"
python3 -m mini_agent.main "read nginx log"
python3 -m mini_agent.main "apply deployment fix"
```

默认模型是 Ollama 中的 `deepseek-v4-flash:cloud`。

## 使用 Ollama

先确认 Ollama 已启动，并且模型可用：

```bash
ollama serve
ollama list
```

运行：

```bash
python3 -m mini_agent.main "check cluster status"
```

也可以换成本机已有模型：

```bash
python3 -m mini_agent.main "grep nginx errors" \
  --ollama-model qwen3.6:27b
```

Ollama adapter 使用本地 HTTP `/api/chat`，要求模型返回严格 JSON：

```json
{"action":"final","content":"..."}
```

或：

```json
{"action":"tool_call","name":"kubectl_get","arguments":{"resource":"pods"}}
```

## 当前安全策略

危险工具不会自动执行。

当前危险工具：

- `exec_shell`
- `kubectl_apply`
- `delete_resource`

当模型请求危险工具时，runtime 会记录 approval_required 事件并停止执行。

## 目录结构

```text
mini_agent/
  runtime.py
  context_builder.py
  tool_registry.py
  tool_executor.py
  observation.py
  permission.py
  memory.py
  trace.py
  models.py
  main.py
  tools/
    devops.py
data/
  cluster.json
  nginx.log
traces/
```

## Phase 1 范围

包含：

- 最小 agent loop
- mock tools
- 危险工具审批拦截
- observation 格式化
- JSONL trace
- 简单短期 memory
- error recovery 基础路径

不包含：

- LangGraph
- MCP
- A2A
- 长期 memory
- 多模型路由
- self-evolving
- UI

这些内容后续阶段再加入。
