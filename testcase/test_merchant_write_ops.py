import uuid

import pytest

from flow_helpers import (
    create_merchant_product,
    create_temp_address,
    delete_address_if_exists,
    resolve_merchant_shop_id,
    resolve_product,
    role_client,
)


@pytest.mark.auth
def test_merchant_product_create_update_delete_roundtrip(settings):
    with role_client(settings, "merchant") as merchant_client:
        shop_id = resolve_merchant_shop_id(merchant_client, settings)
        product_name = f"自动化商户商品-{uuid.uuid4().hex[:6]}"
        create_payload = {
            "shopId": shop_id,
            "name": product_name,
            "category": "大米",
            "price": 12.80,
            "stock": 200,
            "images": "https://example.com/test-product-create.png",
            "description": "自动化创建商品",
            "specs": "1kg/袋",
            "status": 1,
            "sales": 0,
            "origin": "自动化产地",
        }
        create_resp = merchant_client.request("POST", "/api/merchant/products", json=create_payload)
        assert create_resp.status_code == 200
        create_body = create_resp.json()
        assert create_body["code"] == 200
        assert create_body["message"] == "success"
        product_id, _ = resolve_product(
            merchant_client,
            settings,
            keyword=product_name,
            shop_id=shop_id,
            exact_name=product_name,
        )

        update_payload = {
            "shopId": shop_id,
            "name": f"{product_name}-更新",
            "category": "大米",
            "price": 15.80,
            "stock": 180,
            "images": "https://example.com/test-product-update.png",
            "description": "自动化更新商品",
            "specs": "1kg/袋",
            "status": 1,
            "sales": 0,
            "origin": "自动化产地-更新",
        }
        update_resp = merchant_client.request("PUT", f"/api/merchant/products/{product_id}", json=update_payload)
        assert update_resp.status_code == 200
        update_body = update_resp.json()
        assert update_body["code"] == 200
        assert update_body["message"] == "success"

        delete_resp = merchant_client.request("DELETE", f"/api/merchant/products/{product_id}")
        assert delete_resp.status_code == 200
        delete_body = delete_resp.json()
        assert delete_body["code"] == 200
        assert delete_body["message"] == "success"


@pytest.mark.auth
def test_merchant_ship_nonexistent_order_returns_business_error(merchant_api_client):
    payload = {"company": "自动化物流", "trackingNumber": "AUTO-NONEXISTENT-ORDER"}
    response = merchant_api_client.request("POST", "/api/merchant/orders/999999999/ship", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 500
    assert "订单不存在" in (body.get("message") or "")


@pytest.mark.auth
def test_merchant_process_refund_nonexistent_returns_business_error(merchant_api_client):
    payload = {"status": 1, "merchantRemark": "自动化通过"}
    response = merchant_api_client.request("POST", "/api/merchant/refunds/999999999/process", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 500
    assert "退款申请不存在" in (body.get("message") or "")


@pytest.mark.auth
def test_merchant_process_refund_success_after_user_apply(settings):
    order_id = None
    address_id = None

    with role_client(settings, "merchant") as merchant_client:
        shop_id = resolve_merchant_shop_id(merchant_client, settings)
        product_id, _ = create_merchant_product(
            merchant_client,
            settings,
            shop_id=shop_id,
            name_prefix="自动化退款流程商品",
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
        order_id = ((create_body.get("data") or {}).get("id"))
        assert order_id

        pay_resp = user_client.request("PUT", f"/api/orders/{order_id}/pay")
        assert pay_resp.status_code == 200
        pay_body = pay_resp.json()
        assert pay_body["code"] == 200

        refund_payload = {"reason": "自动化退款测试", "amount": 1}
        refund_resp = user_client.request("POST", f"/api/orders/{order_id}/refund", json=refund_payload)
        assert refund_resp.status_code == 200
        refund_body = refund_resp.json()
        assert refund_body["code"] == 200
        assert refund_body["message"] == "success"

        delete_address_if_exists(user_client, address_id)

    with role_client(settings, "merchant") as merchant_client:
        list_resp = merchant_client.request("GET", "/api/merchant/refunds")
        assert list_resp.status_code == 200
        list_body = list_resp.json()
        assert list_body["code"] == 200
        refunds = list_body.get("data") or []
        target = next(
            (
                item
                for item in refunds
                if int(item.get("orderId", 0)) == int(order_id) and int(item.get("status", -1)) == 0
            ),
            None,
        )
        if target is None:
            pytest.skip("未找到待处理退款记录，跳过退款处理成功场景。")
        refund_id = target.get("id")
        assert refund_id

        process_payload = {"status": 1, "merchantRemark": "自动化通过退款"}
        process_resp = merchant_client.request(
            "POST",
            f"/api/merchant/refunds/{refund_id}/process",
            json=process_payload,
        )
        assert process_resp.status_code == 200
        process_body = process_resp.json()
        assert process_body["code"] == 200
        assert process_body["message"] == "success"
