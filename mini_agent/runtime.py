from __future__ import annotations

from .context_builder import ContextBuilder
from .memory import MemoryStore
from .models import ModelClient
from .observation import ObservationHandler
from .permission import PermissionGate
from .tool_executor import ToolExecutor
from .tool_registry import ToolRegistry
from .trace import TraceLogger
from .types import Observation


class MiniAgentRuntime:
    def __init__(
        self,
        model: ModelClient,
        registry: ToolRegistry,
        context_builder: ContextBuilder,
        permission_gate: PermissionGate,
        tool_executor: ToolExecutor,
        observation_handler: ObservationHandler,
        memory: MemoryStore,
        trace: TraceLogger,
        max_steps: int = 5,
    ) -> None:
        self.model = model
        self.registry = registry
        self.context_builder = context_builder
        self.permission_gate = permission_gate
        self.tool_executor = tool_executor
        self.observation_handler = observation_handler
        self.memory = memory
        self.trace = trace
        self.max_steps = max_steps

    def run(self, user_input: str, skills: list[str] | None = None) -> str:
        observations: list[Observation] = []
        skills = skills or []

        self.trace.log_event("run_started", {"user_input": user_input})

        for step in range(1, self.max_steps + 1):
            messages = self.context_builder.build(
                user_input=user_input,
                memory=self.memory.load(),
                skills=skills,
                observations=observations,
            )
            self.trace.log_event(
                "context_built",
                {"step": step, "message_count": len(messages), "observation_count": len(observations)},
            )

            response = self.model.invoke(messages=messages, tools=self.registry.schemas())
            self.trace.log_event(
                "model_response",
                {
                    "step": step,
                    "content": response.content,
                    "tool_call": response.tool_call.__dict__ if response.tool_call else None,
                },
            )

            if not response.has_tool_call:
                self.trace.log_event("run_finished", {"step": step, "final_answer": response.content})
                return response.content

            assert response.tool_call is not None
            decision = self.permission_gate.check(response.tool_call)
            self.trace.log_event(
                "permission_checked",
                {
                    "step": step,
                    "tool_call": response.tool_call.__dict__,
                    "decision": decision.__dict__,
                },
            )

            if decision.requires_approval:
                message = f"Approval required for tool '{response.tool_call.name}': {decision.reason}"
                self.trace.log_event("approval_required", {"step": step, "message": message})
                return message

            result = self.tool_executor.execute(response.tool_call)
            observation = self.observation_handler.process(result)
            observations.append(observation)
            self.trace.log_event(
                "tool_result",
                {
                    "step": step,
                    "tool_call": response.tool_call.__dict__,
                    "result": result.__dict__,
                    "observation": observation.__dict__,
                },
            )

        message = f"Stopped after max_steps={self.max_steps}"
        self.trace.log_event("max_steps_reached", {"message": message})
        return message
