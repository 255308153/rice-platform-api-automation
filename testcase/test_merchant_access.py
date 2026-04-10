import pytest


@pytest.mark.auth
def test_user_role_cannot_access_merchant_orders(authed_api_client):
    response = authed_api_client.request("GET", "/api/merchant/orders")
    assert response.status_code in (401, 403)


@pytest.mark.auth
def test_admin_role_cannot_access_merchant_orders(admin_api_client):
    response = admin_api_client.request("GET", "/api/merchant/orders")
    assert response.status_code in (401, 403)


@pytest.mark.auth
def test_merchant_role_can_access_merchant_orders(merchant_api_client):
    response = merchant_api_client.request("GET", "/api/merchant/orders")
    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 200
    assert body["message"] == "success"
    assert isinstance(body.get("data"), list)


@pytest.mark.auth
def test_merchant_role_can_access_refunds(merchant_api_client):
    response = merchant_api_client.request("GET", "/api/merchant/refunds")
    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 200
    assert body["message"] == "success"
    assert isinstance(body.get("data"), list)
