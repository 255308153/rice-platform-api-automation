import pytest

from flow_helpers import create_merchant_product, resolve_merchant_shop_id, role_client
from utils.schema import validate_with_schema


@pytest.mark.auth
def test_product_list_requires_auth(api_client):
    response = api_client.request("GET", "/api/products?page=1&size=5")
    assert response.status_code in (401, 403)


@pytest.mark.smoke
def test_product_list_success(authed_api_client):
    response = authed_api_client.request("GET", "/api/products?page=1&size=5")
    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 200
    assert body["message"] == "success"
    validate_with_schema(body, "products_list_success.json")
    data = body.get("data") or {}
    records = data.get("records") or []
    assert isinstance(records, list)
    if records:
        first = records[0]
        assert first.get("id")
        assert first.get("shopId")
        assert first.get("name")
        assert first.get("status") in (0, 1)


@pytest.mark.smoke
def test_product_detail_success_by_created_product(settings):
    with role_client(settings, "merchant") as merchant_client:
        shop_id = resolve_merchant_shop_id(merchant_client, settings)
        product_id, product_name = create_merchant_product(
            merchant_client,
            settings,
            shop_id=shop_id,
            name_prefix="自动化商品详情",
        )

    with role_client(settings, "user") as user_client:
        response = user_client.request("GET", f"/api/products/{product_id}")
        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 200
        assert body["message"] == "success"
        data = body["data"]
        assert isinstance(data, dict)
        assert int(data.get("id", 0)) == int(product_id)
        assert data.get("name") == product_name
        assert int(data.get("shopId", 0)) == int(shop_id)
