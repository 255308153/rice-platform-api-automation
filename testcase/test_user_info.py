import pytest
from utils import validate_with_schema


@pytest.mark.auth
def test_user_info_requires_auth(api_client):
    response = api_client.request("GET", "/api/user/info")
    assert response.status_code in (401, 403)


@pytest.mark.auth
def test_user_info_success(authed_api_client, settings):
    response = authed_api_client.request("GET", "/api/user/info")
    assert response.status_code == 200

    body = response.json()
    validate_with_schema(body, "user_info_success.json")
    assert body["code"] == 200
    assert body["message"] == "success"
    data = body["data"]
    assert isinstance(data, dict)
    assert data.get("id")
    assert data.get("username") == settings.user_username
    assert data.get("role")
    assert data.get("password") is None


@pytest.mark.auth
@pytest.mark.db
def test_user_info_matches_db_record(authed_api_client, db_client, settings):
    response = authed_api_client.request("GET", "/api/user/info")
    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 200
    api_user = body["data"]

    row = db_client.fetch_one(
        "SELECT id, username, role, status FROM user WHERE username=%s LIMIT 1",
        (settings.user_username,),
    )
    assert row is not None
    assert int(row["id"]) == int(api_user["id"])
    assert row["username"] == api_user["username"]
    assert row["role"] == api_user["role"]
