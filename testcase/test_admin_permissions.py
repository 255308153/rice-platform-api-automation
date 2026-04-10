import pytest


@pytest.mark.auth
def test_user_role_cannot_access_admin_users(authed_api_client):
    response = authed_api_client.request("GET", "/api/admin/users?page=1&size=5")
    assert response.status_code in (401, 403)


@pytest.mark.auth
def test_admin_role_can_access_admin_users(admin_api_client):
    response = admin_api_client.request("GET", "/api/admin/users?page=1&size=5")
    assert response.status_code == 200

    body = response.json()
    assert body["code"] == 200
    assert body["message"] == "success"
    data = body["data"]
    assert isinstance(data, dict)
    assert isinstance(data.get("records"), list)
