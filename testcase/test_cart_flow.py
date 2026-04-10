import pytest

from flow_helpers import resolve_product


@pytest.mark.auth
def test_cart_add_list_update_delete_clear_flow(authed_api_client, settings):
    product_id, _ = resolve_product(authed_api_client, settings)

    clear_before = authed_api_client.request("DELETE", "/api/cart/clear")
    assert clear_before.status_code == 200
    clear_before_body = clear_before.json()
    assert clear_before_body["code"] == 200

    add_resp = authed_api_client.request(
        "POST",
        "/api/cart/add",
        json={"productId": product_id, "quantity": 2},
    )
    assert add_resp.status_code == 200
    add_body = add_resp.json()
    assert add_body["code"] == 200
    assert add_body["message"] == "success"

    list_resp = authed_api_client.request("GET", "/api/cart/list")
    assert list_resp.status_code == 200
    list_body = list_resp.json()
    assert list_body["code"] == 200
    assert list_body["message"] == "success"
    carts = list_body.get("data") or []
    target = next((item for item in carts if int(item.get("productId", 0)) == int(product_id)), None)
    assert target is not None
    cart_id = target.get("id")
    assert cart_id
    assert int(target.get("quantity", 0)) >= 2

    update_resp = authed_api_client.request("PUT", f"/api/cart/{cart_id}", json={"quantity": 3})
    assert update_resp.status_code == 200
    update_body = update_resp.json()
    assert update_body["code"] == 200
    assert update_body["message"] == "success"

    list_after_update = authed_api_client.request("GET", "/api/cart/list")
    assert list_after_update.status_code == 200
    list_after_update_body = list_after_update.json()
    assert list_after_update_body["code"] == 200
    carts_after_update = list_after_update_body.get("data") or []
    updated = next((item for item in carts_after_update if int(item.get("id", 0)) == int(cart_id)), None)
    assert updated is not None
    assert int(updated.get("quantity", 0)) == 3

    delete_resp = authed_api_client.request("DELETE", f"/api/cart/{cart_id}")
    assert delete_resp.status_code == 200
    delete_body = delete_resp.json()
    assert delete_body["code"] == 200
    assert delete_body["message"] == "success"

    list_after_delete = authed_api_client.request("GET", "/api/cart/list")
    assert list_after_delete.status_code == 200
    list_after_delete_body = list_after_delete.json()
    assert list_after_delete_body["code"] == 200
    carts_after_delete = list_after_delete_body.get("data") or []
    assert all(int(item.get("id", 0)) != int(cart_id) for item in carts_after_delete)

    add_again = authed_api_client.request(
        "POST",
        "/api/cart/add",
        json={"productId": product_id, "quantity": 1},
    )
    assert add_again.status_code == 200
    add_again_body = add_again.json()
    assert add_again_body["code"] == 200

    clear_after = authed_api_client.request("DELETE", "/api/cart/clear")
    assert clear_after.status_code == 200
    clear_after_body = clear_after.json()
    assert clear_after_body["code"] == 200
    assert clear_after_body["message"] == "success"

    list_after_clear = authed_api_client.request("GET", "/api/cart/list")
    assert list_after_clear.status_code == 200
    list_after_clear_body = list_after_clear.json()
    assert list_after_clear_body["code"] == 200
    assert list_after_clear_body.get("data") == []

