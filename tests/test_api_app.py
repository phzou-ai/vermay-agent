from __future__ import annotations

from dataclasses import dataclass

from fastapi.testclient import TestClient

from vermay_agent.api.app import _router_model_name, create_app
from vermay_agent.api.service import AgentService
from vermay_agent.api.session_store import SessionStore
from vermay_agent.langgraph_runtime.results import RunResult
from vermay_agent.main_agent import MainAgentCore, MainAgentStore, MessageRole
from vermay_agent.storage import AgentStore


class FakeRuntime:
    def __init__(self, responses) -> None:
        self.responses = list(responses)
        self.closed = False

    def start(self, user_input, thread_id=None):
        response = self.responses.pop(0)
        if callable(response):
            return response(thread_id)
        return response

    def resume(self, thread_id, approved, reason=None):
        raise RuntimeError("not used")

    def close(self):
        self.closed = True


@dataclass
class InjectedService:
    closed: bool = False

    def close(self):
        self.closed = True


def completed(answer="done"):
    return lambda thread_id: RunResult(thread_id=thread_id, final_answer=answer)


def make_client(tmp_path, runtime):
    store = AgentStore(tmp_path / "agent.sqlite")
    service = AgentService(
        session_store=SessionStore(store),
        runtime_builder=lambda config: runtime,
    )
    return TestClient(create_app(service=service)), store, service


def test_api_health(tmp_path):
    client, store, service = make_client(tmp_path, FakeRuntime([completed()]))

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    service.close()
    store.close()


def test_api_model_config_returns_primary_and_router_models(tmp_path, monkeypatch):
    config_path = tmp_path / "models.json"
    config_path.write_text(
        """
{
  "primary_model": "main-model",
  "router_model": "router-model",
  "models": {
    "main-model": {
      "provider": "ollama",
      "options": {
        "model": "main:latest",
        "base_url": "http://127.0.0.1:11434",
        "timeout_seconds": 120
      }
    },
    "router-model": {
      "provider": "openai_compatible",
      "options": {
        "model": "router",
        "base_url": "http://localhost:8000/v1"
      }
    }
  }
}
""",
        encoding="utf-8",
    )
    monkeypatch.setattr("vermay_agent.api.app.DEFAULT_MODEL_CONFIG_PATH", config_path)
    client, store, service = make_client(tmp_path, FakeRuntime([completed()]))

    response = client.get("/api/model-config")

    assert response.status_code == 200
    assert response.json() == {
        "primary_model": {
            "name": "main-model",
            "provider": "ollama",
            "model": "main:latest",
            "base_url": "http://127.0.0.1:11434",
            "timeout_seconds": 120,
        },
        "router_model": {
            "name": "router-model",
            "provider": "openai_compatible",
            "model": "router",
            "base_url": "http://localhost:8000/v1",
            "timeout_seconds": None,
        },
        "router_model_overridden": False,
        "config_path": str(config_path),
    }
    service.close()
    store.close()


def test_api_contexts_fall_back_to_first_user_message_as_title(tmp_path):
    legacy_store = AgentStore(tmp_path / "legacy.sqlite")
    service = AgentService(
        session_store=SessionStore(legacy_store),
        runtime_builder=lambda config: FakeRuntime([completed()]),
    )
    main_store_backend = AgentStore(tmp_path / "main.sqlite")
    main_store = MainAgentStore(main_store_backend)
    main_store.create_context(context_id="ctx-1")
    main_store.append_message(
        message_id="msg-user-1",
        context_id="ctx-1",
        role=MessageRole.USER,
        parts=[{"kind": "text", "text": "  First   question\nwith spaces "}],
    )
    core = MainAgentCore(store=main_store, local_message_responder=FakeRuntime([]))
    client = TestClient(create_app(service=service, main_agent_core=core))

    response = client.get("/api/contexts")

    assert response.status_code == 200
    assert response.json()[0]["title"] == "First question with spaces"
    service.close()
    legacy_store.close()
    main_store_backend.close()


def test_api_updates_context_title(tmp_path):
    legacy_store = AgentStore(tmp_path / "legacy.sqlite")
    service = AgentService(
        session_store=SessionStore(legacy_store),
        runtime_builder=lambda config: FakeRuntime([completed()]),
    )
    main_store_backend = AgentStore(tmp_path / "main.sqlite")
    main_store = MainAgentStore(main_store_backend)
    context = main_store.create_context(context_id="ctx-1", title="Original")
    core = MainAgentCore(store=main_store, local_message_responder=FakeRuntime([]))
    client = TestClient(create_app(service=service, main_agent_core=core))

    response = client.patch("/api/contexts/ctx-1", json={"title": "  Renamed   session  "})

    assert response.status_code == 200
    assert response.json()["title"] == "Renamed session"
    assert response.json()["updated_at"] == context.updated_at
    service.close()
    legacy_store.close()
    main_store_backend.close()


def test_router_model_name_loads_env_local(tmp_path, monkeypatch):
    monkeypatch.setattr("vermay_agent.env_config.ROOT", tmp_path)
    config_path = tmp_path / "models.json"
    config_path.write_text(
        """
{
  "primary_model": "local_ollama",
  "router_model": "router-config",
  "models": {
    "local_ollama": {
      "provider": "ollama",
      "options": {}
    },
    "router-config": {
      "provider": "ollama",
      "options": {}
    },
    "router-small": {
      "provider": "ollama",
      "options": {}
    }
  }
}
""",
        encoding="utf-8",
    )
    (tmp_path / ".env.local").write_text(
        "VERMAY_AGENT_ROUTER_MODEL=router-small\n",
        encoding="utf-8",
    )
    monkeypatch.delenv("VERMAY_AGENT_ROUTER_MODEL", raising=False)

    assert _router_model_name(config_path=config_path) == "router-small"


def test_router_model_name_loads_config_fallback(tmp_path, monkeypatch):
    monkeypatch.setattr("vermay_agent.env_config.ROOT", tmp_path)
    config_path = tmp_path / "models.json"
    config_path.write_text(
        """
{
  "primary_model": "local_ollama",
  "router_model": "router-config",
  "models": {
    "local_ollama": {
      "provider": "ollama",
      "options": {}
    },
    "router-config": {
      "provider": "ollama",
      "options": {}
    }
  }
}
""",
        encoding="utf-8",
    )
    monkeypatch.delenv("VERMAY_AGENT_ROUTER_MODEL", raising=False)

    assert _router_model_name(config_path=config_path) == "router-config"


def test_legacy_local_rest_routes_are_not_exposed(tmp_path):
    client, store, service = make_client(tmp_path, FakeRuntime([completed()]))

    legacy_requests = [
        ("post", "/api/sessions", {"json": {"session_id": "session-1"}}),
        ("get", "/api/sessions", {}),
        ("get", "/api/sessions/session-1", {}),
        ("delete", "/api/sessions/session-1", {}),
        ("post", "/api/sessions/session-1/tasks", {"json": {"input": "hello"}}),
        ("get", "/api/tasks/task-1", {}),
        ("get", "/api/tasks/task-1/events", {}),
        ("get", "/api/tasks/task-1/artifacts", {}),
        ("get", "/api/tasks/task-1/artifacts/task-1:final_answer", {}),
        ("get", "/api/tasks/task-1/stream", {}),
        ("post", "/api/tasks/task-1/resume", {"json": {"approved": True}}),
        ("post", "/api/tasks/task-1/cancel", {"json": {"reason": "operator"}}),
        ("post", "/api/tasks/task-1/retry", {"json": {"reason": "try again"}}),
    ]

    for method, path, kwargs in legacy_requests:
        response = getattr(client, method)(path, **kwargs)
        assert response.status_code == 404, path
        assert response.json() == {"detail": "Not Found"}

    service.close()
    store.close()


def test_unprefixed_local_rest_routes_are_not_exposed(tmp_path):
    client, store, service = make_client(tmp_path, FakeRuntime([completed()]))

    assert client.get("/sessions").status_code == 404
    assert client.get("/sessions").json() == {"detail": "Not Found"}
    assert client.get("/tasks/task-1").status_code == 404

    service.close()
    store.close()


def test_create_app_does_not_close_injected_service_on_shutdown():
    service = InjectedService()

    with TestClient(create_app(service=service)) as client:
        assert client.get("/health").status_code == 200

    assert service.closed is False
