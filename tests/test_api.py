from fastapi.testclient import TestClient

from mock_openai_api import MOCK_MODEL_ID, MOCK_RESPONSE, app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_list_models():
    response = client.get("/v1/models")
    assert response.status_code == 200
    data = response.json()
    assert data["object"] == "list"
    assert len(data["data"]) == 1
    assert data["data"][0]["id"] == MOCK_MODEL_ID
    assert data["data"][0]["owned_by"] == "devops-exam"


def test_chat_completions():
    response = client.post(
        "/v1/chat/completions",
        json={
            "model": MOCK_MODEL_ID,
            "messages": [{"role": "user", "content": "Hello!"}],
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["object"] == "chat.completion"
    assert data["model"] == MOCK_MODEL_ID
    assert len(data["choices"]) == 1
    assert data["choices"][0]["message"]["role"] == "assistant"
    assert data["choices"][0]["message"]["content"] == MOCK_RESPONSE
    assert data["choices"][0]["finish_reason"] == "stop"


def test_chat_completions_has_usage():
    response = client.post(
        "/v1/chat/completions",
        json={
            "model": MOCK_MODEL_ID,
            "messages": [{"role": "user", "content": "test"}],
        },
    )
    data = response.json()
    assert "usage" in data
    assert "prompt_tokens" in data["usage"]
    assert "completion_tokens" in data["usage"]
    assert "total_tokens" in data["usage"]


def test_chat_completions_unique_ids():
    r1 = client.post(
        "/v1/chat/completions",
        json={"model": MOCK_MODEL_ID, "messages": [{"role": "user", "content": "a"}]},
    )
    r2 = client.post(
        "/v1/chat/completions",
        json={"model": MOCK_MODEL_ID, "messages": [{"role": "user", "content": "b"}]},
    )
    assert r1.json()["id"] != r2.json()["id"]


def test_chat_completions_default_model():
    response = client.post(
        "/v1/chat/completions",
        json={"messages": [{"role": "user", "content": "hi"}]},
    )
    assert response.status_code == 200
    assert response.json()["model"] == MOCK_MODEL_ID
