from __future__ import annotations

from .tool_registry import ToolRegistry
from .tool_metadata import ApprovalPolicy, ToolCategory
from .types import PermissionDecision, ToolCall


class PermissionPolicy:
    def __init__(self, registry: ToolRegistry) -> None:
        self.registry = registry

    def check(self, tool_call: ToolCall) -> PermissionDecision:
        try:
            metadata = self.registry.tool_metadata(tool_call.name)
        except KeyError:
            return PermissionDecision(
                allowed=False,
                requires_approval=False,
                reason=f"unknown tool: {tool_call.name}",
                decision="deny",
                risk_level="high",
                policy_tags=["unknown_tool"],
            )

        if metadata.approval_policy == ApprovalPolicy.DENY:
            return PermissionDecision(
                allowed=False,
                requires_approval=False,
                reason=f"tool '{tool_call.name}' is denied by policy",
                decision="deny",
                risk_level="high",
                policy_tags=["policy_deny"],
            )

        if metadata.approval_policy == ApprovalPolicy.ARGUMENT_SENSITIVE:
            argument_decision = _argument_sensitive_decision(tool_call, metadata.category)
            if argument_decision is not None:
                return argument_decision

        if metadata.approval_policy == ApprovalPolicy.APPROVAL_REQUIRED:
            return PermissionDecision(
                allowed=False,
                requires_approval=True,
                reason=_approval_reason(tool_call.name, metadata.approval_policy),
                decision="interrupt_for_approval",
                risk_level="high" if metadata.dangerous or metadata.destructive else "medium",
                approval_summary=f"Approve tool call: {tool_call.name}",
                safe_argument_preview=dict(tool_call.arguments),
                policy_tags=[metadata.category.value, metadata.approval_policy.value],
            )

        return PermissionDecision(
            allowed=True,
            requires_approval=False,
            reason="safe tool",
            decision="allow",
            risk_level="low",
            policy_tags=[metadata.category.value, metadata.approval_policy.value],
        )


class PermissionGate:
    def __init__(self, registry: ToolRegistry, policy: PermissionPolicy | None = None) -> None:
        self.registry = registry
        self.policy = policy or PermissionPolicy(registry)

    def check(self, tool_call: ToolCall) -> PermissionDecision:
        return self.policy.check(tool_call)


def _argument_sensitive_decision(tool_call: ToolCall, category: ToolCategory) -> PermissionDecision | None:
    if category == ToolCategory.FILESYSTEM and tool_call.name == "read_file":
        path = str(tool_call.arguments.get("path") or "")
        if _is_sensitive_file_path(path):
            return PermissionDecision(
                allowed=False,
                requires_approval=True,
                reason=f"tool '{tool_call.name}' requires approval for sensitive path",
                decision="interrupt_for_approval",
                risk_level="medium",
                approval_summary=f"Read sensitive local file: {path}",
                safe_argument_preview={"path": path},
                policy_tags=[category.value, ApprovalPolicy.ARGUMENT_SENSITIVE.value, "sensitive_path"],
            )
        return PermissionDecision(
            allowed=True,
            requires_approval=False,
            reason="safe tool",
            decision="allow",
            risk_level="low",
            policy_tags=[category.value, ApprovalPolicy.ARGUMENT_SENSITIVE.value],
        )
    return None


def _is_sensitive_file_path(path: str) -> bool:
    normalized = path.replace("\\", "/").strip().lower()
    parts = [part for part in normalized.split("/") if part]
    filename = parts[-1] if parts else normalized
    sensitive_names = {
        ".env",
        ".env.local",
        ".envrc",
        "id_rsa",
        "id_dsa",
        "id_ecdsa",
        "id_ed25519",
        "known_hosts",
    }
    sensitive_terms = ("credential", "credentials", "secret", "secrets", "token", "tokens", "private_key")
    if filename in sensitive_names:
        return True
    if filename.startswith(".env."):
        return True
    return any(term in normalized for term in sensitive_terms)


def _approval_reason(tool_name: str, approval_policy: ApprovalPolicy) -> str:
    if approval_policy == ApprovalPolicy.ARGUMENT_SENSITIVE:
        return f"tool '{tool_name}' requires argument-sensitive approval"
    return f"tool '{tool_name}' is marked dangerous"
