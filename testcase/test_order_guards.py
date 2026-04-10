import pytest


@pytest.mark.auth
def test_order_page_success(authed_api_client):
    response = authed_api_client.request("GET", "/api/orders/page?page=1&size=5&status=-1")
    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 200
    assert body["message"] == "success"
    data = body["data"]
    assert isinstance(data, dict)
    assert isinstance(data.get("records"), list)
    assert int(data.get("size", 0)) == 5


@pytest.mark.auth
def test_refund_list_success(authed_api_client):
    response = authed_api_client.request("GET", "/api/orders/refunds")
    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 200
    assert body["message"] == "success"
    assert isinstance(body.get("data"), list)


@pytest.mark.auth
def test_pay_nonexistent_order_returns_business_error(authed_api_client):
    response = authed_api_client.request("PUT", "/api/orders/999999999/pay")
    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 500
    assert "订单不存在" in (body.get("message") or "")


@pytest.mark.auth
def test_refund_nonexistent_order_returns_business_error(authed_api_client):
    payload = {"reason": "自动化异常路径校验", "amount": 1}
    response = authed_api_client.request("POST", "/api/orders/999999999/refund", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 500
    assert "订单不存在" in (body.get("message") or "")
