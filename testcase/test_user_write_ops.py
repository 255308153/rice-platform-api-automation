import uuid

import pytest


@pytest.mark.auth
def test_register_success_with_unique_username(api_client):
    suffix = uuid.uuid4().hex[:8]
    payload = {
        "username": f"auto_user_{suffix}",
        "password": "123456",
        "phone": f"138{uuid.uuid4().int % 10**8:08d}",
    }
    response = api_client.request("POST", "/api/auth/register", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 200
    assert body["message"] == "success"
    token = ((body.get("data") or {}).get("token") or "").strip()
    assert token
    assert token.count(".") == 2


@pytest.mark.auth
def test_update_user_info_phone_roundtrip(authed_api_client):
    phone = f"139{uuid.uuid4().int % 10**8:08d}"
    update_payload = {"phone": phone}

    update_resp = authed_api_client.request("PUT", "/api/user/info", json=update_payload)
    assert update_resp.status_code == 200
    update_body = update_resp.json()
    assert update_body["code"] == 200
    assert update_body["message"] == "success"

    get_resp = authed_api_client.request("GET", "/api/user/info")
    assert get_resp.status_code == 200
    get_body = get_resp.json()
    assert get_body["code"] == 200
    assert get_body["message"] == "success"
    data = get_body.get("data") or {}
    assert data.get("phone") == phone

