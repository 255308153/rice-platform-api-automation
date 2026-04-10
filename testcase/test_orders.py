import pytest


@pytest.mark.auth
def test_order_list_requires_auth(api_client):
    response = api_client.request("GET", "/api/orders")
    assert response.status_code in (401, 403)


@pytest.mark.smoke
def test_order_list_success(authed_api_client):
    response = authed_api_client.request("GET", "/api/orders")
    assert response.status_code == 200

    body = response.json()
    assert body["code"] == 200
    assert body["message"] == "success"
    assert isinstance(body.get("data"), list)
