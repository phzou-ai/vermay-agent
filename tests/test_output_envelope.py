import pytest

from vermay_agent.api.output_envelope import (
    A2A_PROJECTABLE_KINDS,
    ENVELOPE_VERSION,
    LOCAL_API_PROJECTABLE_KINDS,
    OutputKind,
    OutputVisibility,
    RedactionStatus,
    UI_PROJECTABLE_KINDS,
    final_answer_envelope,
    is_projectable_to_a2a,
    is_projectable_to_local_api,
    normalize_output_metadata,
    summarize_tool_observation,
    tool_observation_envelope,
)


class NonJsonSerializable:
    def __str__(self) -> str:
        return "fallback text"


def test_final_answer_envelope_metadata_shape():
    metadata = final_answer_envelope().to_metadata()

    assert metadata == {
        "envelope_version": ENVELOPE_VERSION,
        "kind": OutputKind.FINAL_ANSWER.value,
        "source": "model",
        "visibility": OutputVisibility.PUBLIC.value,
        "redaction_status": RedactionStatus.CLEAN.value,
        "truncated": False,
        "summary": None,
        "artifact_refs": [],
        "trace_refs": [],
    }


def test_a2a_projection_compatibility_accepts_final_answer_envelope_and_legacy_metadata():
    assert is_projectable_to_a2a(final_answer_envelope().to_metadata()) is True
    assert is_projectable_to_a2a({"kind": "final_answer"}) is True
    assert normalize_output_metadata({"kind": "final_answer"}) == final_answer_envelope().to_metadata()


def test_a2a_projection_rejects_unsafe_or_internal_envelope_metadata():
    unsafe = final_answer_envelope().to_metadata()
    unsafe["redaction_status"] = RedactionStatus.UNSAFE.value

    internal = final_answer_envelope().to_metadata()
    internal["visibility"] = OutputVisibility.INTERNAL.value

    assert is_projectable_to_a2a(unsafe) is False
    assert is_projectable_to_a2a(internal) is False


def test_tool_observation_envelope_defaults_to_internal_unknown_output():
    metadata = tool_observation_envelope(summary="kubectl output", truncated=False).to_metadata()

    assert metadata["kind"] == OutputKind.TOOL_OBSERVATION.value
    assert metadata["source"] == "tool"
    assert metadata["visibility"] == OutputVisibility.INTERNAL.value
    assert metadata["redaction_status"] == RedactionStatus.UNKNOWN.value
    assert metadata["summary"] == "kubectl output"
    assert metadata["truncated"] is False
    assert is_projectable_to_a2a(metadata) is False


def test_tool_observation_is_not_a2a_projectable_without_explicit_future_policy():
    metadata = tool_observation_envelope(
        summary="safe summary",
        truncated=False,
        visibility=OutputVisibility.PUBLIC,
        redaction_status=RedactionStatus.CLEAN,
    ).to_metadata()

    assert is_projectable_to_a2a(metadata) is False
    assert is_projectable_to_local_api(metadata) is False


def test_summarize_tool_observation_serializes_and_truncates_content():
    summary, truncated = summarize_tool_observation({"b": 2, "a": 1}, max_chars=100)
    short_summary, short_truncated = summarize_tool_observation("abcdef", max_chars=3)

    assert summary == '{"a": 1, "b": 2}'
    assert truncated is False
    assert short_summary == "abc\n...<truncated>"
    assert short_truncated is True


def test_summarize_tool_observation_falls_back_for_non_json_serializable_content():
    summary, truncated = summarize_tool_observation(NonJsonSerializable(), max_chars=100)

    assert summary == "fallback text"
    assert truncated is False


def test_summarize_tool_observation_handles_bytes_like_content():
    summary, truncated = summarize_tool_observation(b"hello \xff", max_chars=100)
    bytearray_summary, _ = summarize_tool_observation(bytearray(b"abc"), max_chars=100)
    memoryview_summary, _ = summarize_tool_observation(memoryview(b"xyz"), max_chars=100)

    assert summary == "hello �"
    assert truncated is False
    assert bytearray_summary == "abc"
    assert memoryview_summary == "xyz"


def test_summarize_tool_observation_rejects_non_positive_max_chars():
    with pytest.raises(ValueError, match="max_chars must be positive"):
        summarize_tool_observation("abc", max_chars=0)


def test_projection_uses_explicit_projectable_kind_allowlists():
    assert A2A_PROJECTABLE_KINDS == frozenset({OutputKind.FINAL_ANSWER.value})
    assert LOCAL_API_PROJECTABLE_KINDS == frozenset({OutputKind.FINAL_ANSWER.value})
    assert UI_PROJECTABLE_KINDS == frozenset()
    assert is_projectable_to_local_api(final_answer_envelope().to_metadata()) is True
