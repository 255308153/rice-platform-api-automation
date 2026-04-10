import pytest


@pytest.mark.auth
def test_user_role_cannot_access_admin_comment_audit(authed_api_client):
    response = authed_api_client.request("GET", "/api/admin/content/comments?page=1&size=5")
    assert response.status_code in (401, 403)


@pytest.mark.auth
def test_admin_role_can_access_comment_audit_list(admin_api_client):
    response = admin_api_client.request("GET", "/api/admin/content/comments?page=1&size=5")
    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 200
    assert body["message"] == "success"
    data = body["data"]
    assert isinstance(data, dict)
    assert isinstance(data.get("records"), list)


@pytest.mark.auth
def test_admin_can_get_forum_categories(admin_api_client):
    response = admin_api_client.request("GET", "/api/admin/forum/categories")
    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 200
    assert body["message"] == "success"
    assert isinstance(body.get("data"), list)


@pytest.mark.auth
def test_admin_can_get_notice_list(admin_api_client):
    response = admin_api_client.request("GET", "/api/admin/notices?limit=5")
    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 200
    assert body["message"] == "success"
    assert isinstance(body.get("data"), list)
