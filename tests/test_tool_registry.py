import pytest
from pydantic import Field

from mini_agent.tool_registry import ToolRegistry
from mini_agent.tooling import ToolArgs, structured_tool


class SampleArgs(ToolArgs):
    value: str = Field(description="Sample value.")


def make_sample_tool(dangerous: bool = False):
    return structured_tool(
        func=lambda value: value,
        name="sample",
        description="Sample tool.",
        args_schema=SampleArgs,
        dangerous=dangerous,
    )


def test_registry_exposes_schema_from_structured_tool_args_schema():
    registry = ToolRegistry()
    registry.register(make_sample_tool())

    schema = registry.schemas()[0]

    assert registry.names() == ["sample"]
    assert schema["name"] == "sample"
    assert schema["description"] == "Sample tool."
    assert schema["dangerous"] is False
    assert schema["parameters"]["properties"]["value"]["type"] == "string"
    assert schema["parameters"]["properties"]["value"]["description"] == "Sample value."
    assert schema["parameters"]["required"] == ["value"]


def test_registry_exposes_dangerous_metadata():
    registry = ToolRegistry()
    registry.register(make_sample_tool(dangerous=True))

    assert registry.is_dangerous("sample") is True
    assert registry.schemas()[0]["dangerous"] is True


def test_registry_rejects_duplicate_tool_names():
    registry = ToolRegistry()
    tool = make_sample_tool()

    registry.register(tool)

    with pytest.raises(ValueError, match="tool already registered: sample"):
        registry.register(tool)


def test_registry_unknown_tool_has_clear_error():
    registry = ToolRegistry()

    with pytest.raises(KeyError, match="unknown tool: missing"):
        registry.get("missing")
