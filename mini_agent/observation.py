from __future__ import annotations

import json

from .types import Observation, ToolResult


class ObservationHandler:
    def process(self, result: ToolResult) -> Observation:
        if result.ok:
            content = self._format_output(result.output)
        else:
            content = f"TOOL_ERROR: {result.error}"

        return Observation(tool_name=result.name, content=content, ok=result.ok)

    def _format_output(self, output: object) -> str:
        if isinstance(output, str):
            return output[:4000]
        return json.dumps(output, ensure_ascii=False, indent=2)[:4000]

