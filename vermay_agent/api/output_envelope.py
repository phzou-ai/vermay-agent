from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


ENVELOPE_VERSION = 1
DEFAULT_TOOL_OBSERVATION_SUMMARY_MAX_CHARS = 1000
A2A_PROJECTABLE_KINDS = frozenset({"final_answer"})
LOCAL_API_PROJECTABLE_KINDS = frozenset({"final_answer"})
UI_PROJECTABLE_KINDS = frozenset()


class OutputKind(str, Enum):
    FINAL_ANSWER = "final_answer"
    STATUS_UPDATE = "status_update"
    ARTIFACT_UPDATE = "artifact_update"
    TOOL_OBSERVATION = "tool_observation"
    ERROR_SUMMARY = "error_summary"
    OPERATOR_MESSAGE = "operator_message"


class OutputVisibility(str, Enum):
    PUBLIC = "public"
    LOCAL_API = "local_api"
    A2A = "a2a"
    UI = "ui"
    INTERNAL = "internal"
    TRACE_ONLY = "trace_only"


class RedactionStatus(str, Enum):
    CLEAN = "clean"
    REDACTED = "redacted"
    UNSAFE = "unsafe"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class OutputEnvelope:
    kind: OutputKind
    source: str
    visibility: OutputVisibility
    redaction_status: RedactionStatus
    truncated: bool = False
    summary: str | None = None
    artifact_refs: list[str] = field(default_factory=list)
    trace_refs: list[str] = field(default_factory=list)
    envelope_version: int = ENVELOPE_VERSION

    def to_metadata(self) -> dict[str, Any]:
        return {
            "envelope_version": self.envelope_version,
            "kind": self.kind.value,
            "source": self.source,
            "visibility": self.visibility.value,
            "redaction_status": self.redaction_status.value,
            "truncated": self.truncated,
            "summary": self.summary,
            "artifact_refs": list(self.artifact_refs),
            "trace_refs": list(self.trace_refs),
        }


def final_answer_envelope() -> OutputEnvelope:
    return OutputEnvelope(
        kind=OutputKind.FINAL_ANSWER,
        source="model",
        visibility=OutputVisibility.PUBLIC,
        redaction_status=RedactionStatus.CLEAN,
    )


def tool_observation_envelope(
    *,
    summary: str | None,
    truncated: bool,
    visibility: OutputVisibility = OutputVisibility.INTERNAL,
    redaction_status: RedactionStatus = RedactionStatus.UNKNOWN,
) -> OutputEnvelope:
    return OutputEnvelope(
        kind=OutputKind.TOOL_OBSERVATION,
        source="tool",
        visibility=visibility,
        redaction_status=redaction_status,
        truncated=truncated,
        summary=summary,
    )


def summarize_tool_observation(
    content: Any,
    *,
    max_chars: int = DEFAULT_TOOL_OBSERVATION_SUMMARY_MAX_CHARS,
) -> tuple[str, bool]:
    if max_chars < 1:
        raise ValueError("max_chars must be positive")
    text = _stringify_summary_content(content)
    if len(text) <= max_chars:
        return text, False
    return text[:max_chars] + "\n...<truncated>", True


def is_projectable_to_a2a(metadata: dict[str, Any]) -> bool:
    kind = metadata.get("kind")
    if metadata.get("envelope_version") is None:
        return kind in A2A_PROJECTABLE_KINDS
    return (
        kind in A2A_PROJECTABLE_KINDS
        and metadata.get("visibility") in {OutputVisibility.PUBLIC.value, OutputVisibility.A2A.value}
        and metadata.get("redaction_status") in {RedactionStatus.CLEAN.value, RedactionStatus.REDACTED.value}
    )


def is_projectable_to_local_api(metadata: dict[str, Any]) -> bool:
    kind = metadata.get("kind")
    if metadata.get("envelope_version") is None:
        return kind in LOCAL_API_PROJECTABLE_KINDS
    return (
        kind in LOCAL_API_PROJECTABLE_KINDS
        and metadata.get("visibility") in {OutputVisibility.PUBLIC.value, OutputVisibility.LOCAL_API.value}
        and metadata.get("redaction_status") in {RedactionStatus.CLEAN.value, RedactionStatus.REDACTED.value}
    )


def normalize_output_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
    if metadata.get("envelope_version") is not None:
        return dict(metadata)
    if metadata.get("kind") == OutputKind.FINAL_ANSWER.value:
        return final_answer_envelope().to_metadata()
    return dict(metadata)


def _stringify_summary_content(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, bytes):
        return content.decode("utf-8", errors="replace")
    if isinstance(content, bytearray):
        return bytes(content).decode("utf-8", errors="replace")
    if isinstance(content, memoryview):
        return content.tobytes().decode("utf-8", errors="replace")
    try:
        return json.dumps(content, ensure_ascii=False, sort_keys=True)
    except (TypeError, ValueError):
        try:
            return str(content)
        except Exception:
            return f"<unprintable {type(content).__name__}>"
