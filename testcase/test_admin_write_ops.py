import uuid

import pytest


@pytest.mark.auth
def test_admin_config_set_and_get_roundtrip(admin_api_client):
    key = "auto_test_runtime_flag"
    value = f"v-{uuid.uuid4().hex[:8]}"
    payload = {"key": key, "value": value, "description": "自动化测试临时配置"}

    set_resp = admin_api_client.request("PUT", "/api/admin/config", json=payload)
    assert set_resp.status_code == 200
    set_body = set_resp.json()
    assert set_body["code"] == 200
    assert set_body["message"] == "success"

    get_resp = admin_api_client.request("GET", f"/api/admin/config/{key}")
    assert get_resp.status_code == 200
    get_body = get_resp.json()
    assert get_body["code"] == 200
    assert get_body["message"] == "success"
    assert get_body.get("data") == value


@pytest.mark.auth
def test_admin_notice_create_and_delete_roundtrip(admin_api_client):
    title = f"自动化公告-{uuid.uuid4().hex[:8]}"
    content = "这是一条自动化测试公告，用于回归验证公告增删流程。"
    payload = {"title": title, "content": content, "role": "ALL"}

    create_resp = admin_api_client.request("POST", "/api/admin/notices", json=payload)
    assert create_resp.status_code == 200
    create_body = create_resp.json()
    assert create_body["code"] == 200
    assert create_body["message"] == "success"

    list_resp = admin_api_client.request("GET", "/api/admin/notices?limit=100")
    assert list_resp.status_code == 200
    list_body = list_resp.json()
    assert list_body["code"] == 200
    notices = list_body.get("data") or []
    created = next((n for n in notices if n.get("title") == title), None)
    assert created is not None
    notice_id = created.get("id")
    assert notice_id

    delete_resp = admin_api_client.request("DELETE", f"/api/admin/notices/{notice_id}")
    assert delete_resp.status_code == 200
    delete_body = delete_resp.json()
    assert delete_body["code"] == 200
    assert delete_body["message"] == "success"

    verify_resp = admin_api_client.request("GET", "/api/admin/notices?limit=100")
    assert verify_resp.status_code == 200
    verify_body = verify_resp.json()
    assert verify_body["code"] == 200
    ids = {n.get("id") for n in (verify_body.get("data") or [])}
    assert notice_id not in ids
