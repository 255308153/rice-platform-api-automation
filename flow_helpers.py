from __future__ import annotations

from contextlib import contextmanager
import uuid
from typing import Iterator

import pytest

from clients import APIClient, DBClient
from config import ApiTestSettings


def _query_one_if_configured(
    settings: ApiTestSettings, sql: str, params: tuple[object, ...] | None = None
) -> dict | None:
    if not (settings.db_host and settings.db_user and settings.db_name):
        return None
    db = DBClient(
        host=settings.db_host,
        port=settings.db_port,
        user=settings.db_user,
        password=settings.db_password,
        database=settings.db_name,
    )
    try:
        db.connect()
        return db.fetch_one(sql, params or ())
    except Exception:
        return None
    finally:
        db.close()


def _get_role_credentials(settings: ApiTestSettings, role: str) -> tuple[str, str, str]:
    role_name = role.strip().lower()
    if role_name == "user":
        return settings.user_username, settings.user_password, "用户"
    if role_name == "admin":
        return settings.admin_username, settings.admin_password, "管理员"
    if role_name == "merchant":
        return settings.merchant_username, settings.merchant_password, "商户"
    raise ValueError(f"不支持的角色：{role}")


def _login_and_set_token(client: APIClient, settings: ApiTestSettings, role: str) -> None:
    username, password, role_label = _get_role_credentials(settings, role)
    if not username or not password:
        pytest.skip(f"未配置{role_label}账号环境变量，跳过该场景。")

    resp = client.login(username, password)
    if resp.status_code != 200:
        pytest.skip(f"{role_label}登录接口异常，HTTP={resp.status_code}")
    body = resp.json()
    if body.get("code") != 200:
        pytest.skip(f"{role_label}登录失败，message={body.get('message')}")

    token = ((body.get("data") or {}).get("token") or "").strip()
    if not token:
        pytest.skip(f"{role_label}登录成功但未返回 token。")
    client.set_bearer_token(token)


@contextmanager
def role_client(settings: ApiTestSettings, role: str) -> Iterator[APIClient]:
    client = APIClient(settings.base_url, settings.timeout_seconds)
    try:
        _login_and_set_token(client, settings, role)
        yield client
    finally:
        client.close()


def resolve_merchant_shop_id(merchant_client: APIClient, settings: ApiTestSettings) -> int:
    warm_up = merchant_client.request("GET", "/api/merchant/orders")
    assert warm_up.status_code == 200
    warm_body = warm_up.json()
    if warm_body.get("code") != 200:
        pytest.skip(f"商户订单接口不可用，message={warm_body.get('message')}")

    info_resp = merchant_client.request("GET", "/api/user/info")
    assert info_resp.status_code == 200
    info_body = info_resp.json()
    if info_body.get("code") != 200:
        pytest.skip(f"无法获取商户用户信息，message={info_body.get('message')}")

    merchant_id = ((info_body.get("data") or {}).get("id"))
    if not merchant_id:
        pytest.skip("商户用户信息缺少 id，无法定位店铺。")

    shop_resp = merchant_client.request("GET", f"/api/shops/user/{merchant_id}")
    if shop_resp.status_code == 200:
        shop_body = shop_resp.json()
        if shop_body.get("code") == 200:
            shop_data = shop_body.get("data") or {}
            if shop_data.get("id"):
                return int(shop_data["id"])

    row = _query_one_if_configured(
        settings,
        "SELECT id FROM shop WHERE user_id=%s ORDER BY id DESC LIMIT 1",
        (merchant_id,),
    )
    if row and row.get("id"):
        return int(row["id"])

    pytest.skip("无法定位商户店铺ID（/api/shops/user 或 DB 均未获取到）。")


def resolve_product(
    authed_client: APIClient,
    settings: ApiTestSettings,
    *,
    keyword: str | None = None,
    shop_id: int | None = None,
    exact_name: str | None = None,
) -> tuple[int, int]:
    path = "/api/products?page=1&size=20"
    if keyword:
        path += f"&keyword={keyword}"
    if shop_id:
        path += f"&shopId={shop_id}"

    list_resp = authed_client.request("GET", path)
    if list_resp.status_code == 200:
        body = list_resp.json()
        if body.get("code") == 200:
            records = ((body.get("data") or {}).get("records") or [])
            for item in records:
                pid = item.get("id")
                sid = item.get("shopId")
                name = item.get("name")
                if not pid or not sid:
                    continue
                if exact_name and name != exact_name:
                    continue
                if shop_id and int(sid) != int(shop_id):
                    continue
                return int(pid), int(sid)

    sql = "SELECT id, shop_id FROM product WHERE status=1"
    params: tuple[object, ...] = ()
    where = []
    if exact_name:
        where.append("name=%s")
        params += (exact_name,)
    if shop_id:
        where.append("shop_id=%s")
        params += (shop_id,)
    if where:
        sql += " AND " + " AND ".join(where)
    sql += " ORDER BY id DESC LIMIT 1"

    row = _query_one_if_configured(settings, sql, params)
    if row and row.get("id") and row.get("shop_id"):
        return int(row["id"]), int(row["shop_id"])

    # 兜底：当前环境没有可用商品时，使用商户账号自动创建一个测试商品，避免流程用例被环境数据阻塞。
    if not exact_name:
        with role_client(settings, "merchant") as merchant_client:
            target_shop_id = shop_id or resolve_merchant_shop_id(merchant_client, settings)
            product_id, _ = create_merchant_product(
                merchant_client,
                settings,
                shop_id=target_shop_id,
                name_prefix="自动化兜底商品",
            )
            return int(product_id), int(target_shop_id)

    pytest.skip("当前环境无法获取可用商品（/api/products 异常且未配置可用 DB 回退）。")


def create_temp_address(user_client: APIClient) -> tuple[int, str]:
    suffix = uuid.uuid4().hex[:8]
    detail = f"自动化地址-{suffix}"
    payload = {
        "name": "自动化收件人",
        "phone": "13800138000",
        "province": "广东省",
        "city": "广州市",
        "district": "天河区",
        "detail": detail,
        "isDefault": 0,
    }
    create_resp = user_client.request("POST", "/api/addresses", json=payload)
    assert create_resp.status_code == 200
    create_body = create_resp.json()
    assert create_body["code"] == 200
    assert create_body["message"] == "success"

    list_resp = user_client.request("GET", "/api/addresses")
    assert list_resp.status_code == 200
    list_body = list_resp.json()
    assert list_body["code"] == 200
    addresses = list_body.get("data") or []
    created = next((item for item in addresses if item.get("detail") == detail), None)
    if not created or not created.get("id"):
        pytest.skip("新增地址后未在列表中找到对应记录。")
    return int(created["id"]), detail


def delete_address_if_exists(user_client: APIClient, address_id: int | None) -> None:
    if not address_id:
        return
    delete_resp = user_client.request("DELETE", f"/api/addresses/{address_id}")
    if delete_resp.status_code != 200:
        return
    body = delete_resp.json()
    if body.get("code") not in (200, 500):
        return


def create_merchant_product(
    merchant_client: APIClient,
    settings: ApiTestSettings,
    *,
    shop_id: int,
    name_prefix: str = "自动化商品",
) -> tuple[int, str]:
    name = f"{name_prefix}-{uuid.uuid4().hex[:8]}"
    payload = {
        "shopId": shop_id,
        "name": name,
        "category": "大米",
        "price": 12.50,
        "stock": 200,
        "images": "https://example.com/test-product.png",
        "description": "自动化测试商品",
        "specs": "500g/袋",
        "status": 1,
        "sales": 0,
        "origin": "自动化产地",
    }
    create_resp = merchant_client.request("POST", "/api/merchant/products", json=payload)
    assert create_resp.status_code == 200
    create_body = create_resp.json()
    assert create_body["code"] == 200
    assert create_body["message"] == "success"

    product_id, _ = resolve_product(
        merchant_client,
        settings,
        keyword=name,
        shop_id=shop_id,
        exact_name=name,
    )
    return product_id, name
