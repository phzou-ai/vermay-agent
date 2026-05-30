# Hands-On LangGraph Runtime Archive

This directory contains the archived hands-on LangGraph runtime.

The archived runtime was used to make harness mechanics explicit:

- context building
- custom model response parsing
- permission checks
- custom tool execution
- observation handling
- graph stream inspection
- JSONL tracing

It is no longer part of the active CLI or default test suite. The project mainline is now `mini_agent/langgraph_runtime/`, which uses LangChain / LangGraph standard message types and `ToolNode`.

Archive layout:

```text
archive/hands_on_langgraph_runtime/
  runtime/           archived implementation
  reference_tests/   archived tests, intentionally not collected by pytest
```

The files in `reference_tests/` are retained as historical reference material. They are named without the `test_` prefix so the active project test suite does not collect them.
