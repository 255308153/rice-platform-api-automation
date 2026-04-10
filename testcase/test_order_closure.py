import uuid

import pytest

from flow_helpers import (
    create_merchant_product,
    create_temp_address,
    delete_address_if_exists,
    resolve_merchant_shop_id,
    role_client,
)


@pytest.mark.auth
def test_order_create_missing_address_returns_business_error(authed_api_client):
    payload = {"shopId": 1, "addressId": None, "items": [{"productId": 1, "quantity": 1}]}
    response = authed_api_client.request("POST", "/api/orders", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 500
    assert "请先选择收货地址" in (body.get("message") or "")


@pytest.mark.auth
def test_order_confirm_nonexistent_returns_business_error(authed_api_client):
    response = authed_api_client.request("PUT", "/api/orders/999999999/confirm")
    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 500
    assert "订单不存在" in (body.get("message") or "")


@pytest.mark.auth
def test_order_review_nonexistent_returns_business_error(authed_api_client):
    payload = {"productId": 1, "rating": 5, "content": "自动化测试评价"}
    response = authed_api_client.request("POST", "/api/orders/999999999/review", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 500
    assert "订单不存在" in (body.get("message") or "")


@pytest.mark.auth
def test_order_closed_loop_create_pay_ship_confirm_review(settings):
    order_id = None
    product_id = None
    address_id = None

    with role_client(settings, "merchant") as merchant_client:
        shop_id = resolve_merchant_shop_id(merchant_client, settings)
        product_id, _ = create_merchant_product(
            merchant_client,
            settings,
            shop_id=shop_id,
            name_prefix="自动化订单闭环商品",
        )

    with role_client(settings, "user") as user_client:
        address_id, _ = create_temp_address(user_client)
        create_payload = {
            "shopId": shop_id,
            "addressId": address_id,
            "items": [{"productId": product_id, "quantity": 1}],
        }
        create_resp = user_client.request("POST", "/api/orders", json=create_payload)
        assert create_resp.status_code == 200
        create_body = create_resp.json()
        assert create_body["code"] == 200
        assert create_body["message"] == "success"
        order = create_body.get("data") or {}
        order_id = order.get("id")
        assert order_id

        pay_resp = user_client.request("PUT", f"/api/orders/{order_id}/pay")
        assert pay_resp.status_code == 200
        pay_body = pay_resp.json()
        assert pay_body["code"] == 200
        assert pay_body["message"] == "success"

    with role_client(settings, "merchant") as merchant_client:
        ship_payload = {
            "company": "自动化物流",
            "trackingNumber": f"AUTO{uuid.uuid4().hex[:10].upper()}",
        }
        ship_resp = merchant_client.request(
            "POST",
            f"/api/merchant/orders/{order_id}/ship",
            json=ship_payload,
        )
        assert ship_resp.status_code == 200
        ship_body = ship_resp.json()
        assert ship_body["code"] == 200
        assert ship_body["message"] == "success"

    with role_client(settings, "user") as user_client:
        confirm_resp = user_client.request("PUT", f"/api/orders/{order_id}/confirm")
        assert confirm_resp.status_code == 200
        confirm_body = confirm_resp.json()
        assert confirm_body["code"] == 200
        assert confirm_body["message"] == "success"

        review_payload = {
            "productId": product_id,
            "rating": 5,
            "content": "自动化闭环评价-流程正常",
        }
        review_resp = user_client.request("POST", f"/api/orders/{order_id}/review", json=review_payload)
        assert review_resp.status_code == 200
        review_body = review_resp.json()
        assert review_body["code"] == 200
        assert review_body["message"] == "success"

        delete_address_if_exists(user_client, address_id)

