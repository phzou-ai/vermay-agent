from __future__ import annotations

from dataclasses import dataclass, field
from uuid import uuid4

from langchain_core.tools import BaseTool
from langgraph.checkpoint.memory import InMemorySaver

from mini_agent.langgraph_runtime.results import RunResult

from .graph import build_standard_graph
from .nodes import StandardGraphComponents, StandardModelClient
from .state import StandardAgentState, build_initial_state


@dataclass
class StandardLangGraphAgentRuntime:
    model: StandardModelClient
    tools: list[BaseTool] = field(default_factory=list)
    system_prompt: str | None = None
    max_loops: int = 5
    checkpointer: object | None = None

    def __post_init__(self) -> None:
        components = StandardGraphComponents(model=self.model, tools=self.tools)
        self.graph = build_standard_graph(components, checkpointer=self.checkpointer or InMemorySaver())

    def run(self, user_input: str, thread_id: str | None = None) -> str:
        return self.start(user_input, thread_id=thread_id).to_output()

    def start(self, user_input: str, thread_id: str | None = None) -> RunResult:
        active_thread_id = thread_id or str(uuid4())
        state = self._initial_state(user_input)
        final_state = self.graph.invoke(state, config=self._config(active_thread_id))

        final_answer = final_state.get("final_answer")
        if final_answer is not None:
            return RunResult(thread_id=active_thread_id, final_answer=final_answer, state=final_state)

        return RunResult(
            thread_id=active_thread_id,
            state=final_state,
            stop_message="Standard runtime stopped without a final answer.",
        )

    def _initial_state(self, user_input: str) -> StandardAgentState:
        return build_initial_state(user_input, system_prompt=self.system_prompt, max_loops=self.max_loops)

    def _config(self, thread_id: str) -> dict:
        return {"configurable": {"thread_id": thread_id}}
