import uuid

import pytest


def _temp_address_payload() -> dict:
    unique_suffix = uuid.uuid4().hex[:8]
    return {
        "name": "自动化收件人",
        "phone": "13800138000",
        "province": "广东省",
        "city": "广州市",
        "district": "天河区",
        "detail": f"自动化测试地址-{unique_suffix}",
        "isDefault": 0,
    }


@pytest.mark.auth
def test_address_list_requires_auth(api_client):
    response = api_client.request("GET", "/api/addresses")
    assert response.status_code in (401, 403)


@pytest.mark.auth
def test_address_list_success(authed_api_client):
    response = authed_api_client.request("GET", "/api/addresses")
    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 200
    assert body["message"] == "success"
    assert isinstance(body.get("data"), list)


@pytest.mark.auth
def test_address_create_and_delete_roundtrip(authed_api_client):
    payload = _temp_address_payload()
    create_resp = authed_api_client.request("POST", "/api/addresses", json=payload)
    assert create_resp.status_code == 200
    create_body = create_resp.json()
    assert create_body["code"] == 200
    assert create_body["message"] == "success"

    list_resp = authed_api_client.request("GET", "/api/addresses")
    assert list_resp.status_code == 200
    list_body = list_resp.json()
    assert list_body["code"] == 200
    addresses = list_body.get("data") or []

    created = next((item for item in addresses if item.get("detail") == payload["detail"]), None)
    assert created is not None
    created_id = created.get("id")
    assert created_id

    delete_resp = authed_api_client.request("DELETE", f"/api/addresses/{created_id}")
    assert delete_resp.status_code == 200
    delete_body = delete_resp.json()
    assert delete_body["code"] == 200
    assert delete_body["message"] == "success"

    verify_resp = authed_api_client.request("GET", "/api/addresses")
    assert verify_resp.status_code == 200
    verify_body = verify_resp.json()
    assert verify_body["code"] == 200
    ids = {item.get("id") for item in (verify_body.get("data") or [])}
    assert created_id not in ids
