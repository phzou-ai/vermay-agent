from __future__ import annotations

import json
from pathlib import Path

from mini_agent.tool_registry import ToolRegistry
from mini_agent.types import ToolSpec


ROOT = Path(__file__).resolve().parents[2]


def read_file(path: str) -> str:
    target = (ROOT / path).resolve()
    if ROOT not in target.parents and target != ROOT:
        raise ValueError("path escapes project root")
    return target.read_text(encoding="utf-8")


def grep_logs(pattern: str) -> dict:
    log_path = ROOT / "data" / "nginx.log"
    lines = log_path.read_text(encoding="utf-8").splitlines()
    matches = [line for line in lines if pattern.lower() in line.lower()]
    return {"pattern": pattern, "matches": matches, "count": len(matches)}


def kubectl_get(resource: str) -> dict:
    cluster = json.loads((ROOT / "data" / "cluster.json").read_text(encoding="utf-8"))
    if resource not in cluster:
        raise ValueError(f"unknown mock resource: {resource}")
    return {resource: cluster[resource]}


def exec_shell(command: str) -> dict:
    return {"command": command, "status": "not_executed_in_demo"}


def kubectl_apply(manifest: str) -> dict:
    return {"manifest": manifest, "status": "not_applied_in_demo"}


def delete_resource(resource: str, name: str) -> dict:
    return {"resource": resource, "name": name, "status": "not_deleted_in_demo"}


def register_devops_tools(registry: ToolRegistry) -> None:
    registry.register(
        ToolSpec(
            name="read_file",
            description="Read a file under the project root.",
            parameters={"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]},
            dangerous=False,
            func=read_file,
        )
    )
    registry.register(
        ToolSpec(
            name="grep_logs",
            description="Search the mock nginx log for a simple substring. Use 'error' to find error lines.",
            parameters={
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "Simple substring such as 'error', 'timeout', or '502'.",
                    }
                },
                "required": ["pattern"],
            },
            dangerous=False,
            func=grep_logs,
        )
    )
    registry.register(
        ToolSpec(
            name="kubectl_get",
            description="Read mock Kubernetes resource state.",
            parameters={
                "type": "object",
                "properties": {"resource": {"type": "string", "enum": ["pods", "services"]}},
                "required": ["resource"],
            },
            dangerous=False,
            func=kubectl_get,
        )
    )
    registry.register(
        ToolSpec(
            name="exec_shell",
            description="Execute a shell command. Dangerous and requires approval.",
            parameters={"type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"]},
            dangerous=True,
            func=exec_shell,
        )
    )
    registry.register(
        ToolSpec(
            name="kubectl_apply",
            description="Apply a Kubernetes manifest. Dangerous and requires approval.",
            parameters={"type": "object", "properties": {"manifest": {"type": "string"}}, "required": ["manifest"]},
            dangerous=True,
            func=kubectl_apply,
        )
    )
    registry.register(
        ToolSpec(
            name="delete_resource",
            description="Delete a Kubernetes resource. Dangerous and requires approval.",
            parameters={
                "type": "object",
                "properties": {"resource": {"type": "string"}, "name": {"type": "string"}},
                "required": ["resource", "name"],
            },
            dangerous=True,
            func=delete_resource,
        )
    )
