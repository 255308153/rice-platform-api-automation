import pytest


@pytest.mark.auth
def test_ai_chat_requires_auth(api_client):
    response = api_client.request("POST", "/api/ai/chat", json={"message": "你好"})
    assert response.status_code in (401, 403)


@pytest.mark.auth
def test_ai_chat_empty_message_returns_business_error(authed_api_client):
    response = authed_api_client.request("POST", "/api/ai/chat", json={"message": "   "})
    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 500
    assert "消息不能为空" in (body.get("message") or "")


@pytest.mark.auth
def test_ai_chat_history_success(authed_api_client):
    response = authed_api_client.request("GET", "/api/ai/chat/history?limit=5")
    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 200
    assert body["message"] == "success"
    assert isinstance(body.get("data"), list)


@pytest.mark.auth
def test_ai_recognition_history_success(authed_api_client):
    response = authed_api_client.request("GET", "/api/ai/recognition/history?limit=5")
    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 200
    assert body["message"] == "success"
    assert isinstance(body.get("data"), list)
