import pytest

from flow_helpers import role_client
from utils.schema import validate_with_schema


@pytest.mark.auth
def test_shop_list_requires_auth(api_client):
    response = api_client.request("GET", "/api/shops?page=1&size=5")
    assert response.status_code in (401, 403)


@pytest.mark.smoke
def test_shop_list_success(authed_api_client):
    response = authed_api_client.request("GET", "/api/shops?page=1&size=5")
    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 200
    assert body["message"] == "success"
    validate_with_schema(body, "shops_list_success.json")
    data = body.get("data") or {}
    records = data.get("records") or []
    assert isinstance(records, list)
    if records:
        first = records[0]
        assert first.get("id")
        assert first.get("userId")
        assert first.get("name")
        assert first.get("status") in (0, 1)


@pytest.mark.smoke
def test_shop_get_by_user_success(settings):
    with role_client(settings, "merchant") as merchant_client:
        me_resp = merchant_client.request("GET", "/api/user/info")
        assert me_resp.status_code == 200
        me_body = me_resp.json()
        assert me_body["code"] == 200
        merchant_id = ((me_body.get("data") or {}).get("id"))
        assert merchant_id

        shop_resp = merchant_client.request("GET", f"/api/shops/user/{merchant_id}")
        assert shop_resp.status_code == 200
        shop_body = shop_resp.json()
        assert shop_body["code"] == 200
        assert shop_body["message"] == "success"
        shop_data = shop_body.get("data") or {}
        assert shop_data.get("id")
        assert int(shop_data.get("userId", 0)) == int(merchant_id)


@pytest.mark.auth
def test_shop_detail_success_from_merchant_shop(settings):
    with role_client(settings, "merchant") as merchant_client:
        me_resp = merchant_client.request("GET", "/api/user/info")
        assert me_resp.status_code == 200
        me_body = me_resp.json()
        assert me_body["code"] == 200
        merchant_id = ((me_body.get("data") or {}).get("id"))
        assert merchant_id

        shop_resp = merchant_client.request("GET", f"/api/shops/user/{merchant_id}")
        assert shop_resp.status_code == 200
        shop_body = shop_resp.json()
        assert shop_body["code"] == 200
        shop_id = ((shop_body.get("data") or {}).get("id"))
        assert shop_id

    with role_client(settings, "user") as user_client:
        detail_resp = user_client.request("GET", f"/api/shops/{shop_id}")
        assert detail_resp.status_code == 200
        detail_body = detail_resp.json()
        assert detail_body["code"] == 200
        assert detail_body["message"] == "success"
        detail_data = detail_body.get("data") or {}
        assert int(detail_data.get("id", 0)) == int(shop_id)
