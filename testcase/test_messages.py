import pytest


@pytest.mark.auth
def test_contacts_requires_auth(api_client):
    response = api_client.request("GET", "/api/messages/contacts")
    assert response.status_code in (401, 403)


@pytest.mark.auth
def test_contacts_list_success(authed_api_client):
    response = authed_api_client.request("GET", "/api/messages/contacts")
    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 200
    assert body["message"] == "success"
    assert isinstance(body.get("data"), list)


@pytest.mark.auth
def test_conversation_list_success(authed_api_client):
    response = authed_api_client.request("GET", "/api/conversations?page=1&size=5")
    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 200
    assert body["message"] == "success"
    data = body.get("data")
    assert isinstance(data, dict)
    assert isinstance(data.get("records"), list)


@pytest.mark.auth
def test_conversation_preferences_roundtrip(authed_api_client):
    payload = {"pinnedIds": ["100", "100", "200"], "hiddenIds": ["200"]}
    save_resp = authed_api_client.request("PUT", "/api/conversations/preferences", json=payload)
    assert save_resp.status_code == 200
    save_body = save_resp.json()
    assert save_body["code"] == 200
    assert save_body["message"] == "success"

    get_resp = authed_api_client.request("GET", "/api/conversations/preferences")
    assert get_resp.status_code == 200
    get_body = get_resp.json()
    assert get_body["code"] == 200
    assert get_body["message"] == "success"
    data = get_body.get("data")
    assert isinstance(data, dict)
    pinned = data.get("pinnedIds") or []
    hidden = data.get("hiddenIds") or []
    assert isinstance(pinned, list)
    assert isinstance(hidden, list)
    assert "200" in hidden
    assert "200" not in pinned


@pytest.mark.auth
def test_send_message_missing_required_fields_returns_business_error(authed_api_client):
    response = authed_api_client.request("POST", "/api/messages", json={})
    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 500
    assert "receiverId 和 content 不能为空" in (body.get("message") or "")
