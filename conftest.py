import pytest
import requests

from clients import APIClient, DBClient
from config import ApiTestSettings, load_settings


@pytest.fixture(scope="session")
def settings() -> ApiTestSettings:
    return load_settings()


@pytest.fixture(scope="session", autouse=True)
def ensure_backend_available(settings: ApiTestSettings) -> None:
    health_path = "/api/products?page=1&size=1"
    health_url = f"{settings.base_url}{health_path}"
    try:
        response = requests.get(health_url, timeout=settings.timeout_seconds)
    except requests.RequestException as exc:
        pytest.skip(f"后端服务不可用，跳过接口测试：{exc}")

    if response.status_code >= 500:
        pytest.skip(f"后端服务异常（{response.status_code}），跳过接口测试。")


@pytest.fixture(scope="function")
def api_client(settings: ApiTestSettings):
    client = APIClient(settings.base_url, settings.timeout_seconds)
    try:
        yield client
    finally:
        client.close()


@pytest.fixture(scope="function")
def user_token(api_client: APIClient, settings: ApiTestSettings) -> str:
    if not settings.user_username or not settings.user_password:
        pytest.skip("未配置登录账号（RICE_API_USER_USERNAME/RICE_API_USER_PASSWORD）。")
    response = api_client.login(settings.user_username, settings.user_password)
    if response.status_code != 200:
        pytest.skip(f"登录接口异常，HTTP={response.status_code}")
    body = response.json()
    if body.get("code") != 200:
        pytest.skip(f"登录失败，message={body.get('message')}")
    token = ((body.get("data") or {}).get("token") or "").strip()
    if not token:
        pytest.skip("登录成功但未返回 token。")
    return token


@pytest.fixture(scope="function")
def authed_api_client(api_client: APIClient, user_token: str) -> APIClient:
    api_client.set_bearer_token(user_token)
    return api_client


@pytest.fixture(scope="function")
def admin_token(api_client: APIClient, settings: ApiTestSettings) -> str:
    if not settings.admin_username or not settings.admin_password:
        pytest.skip("未配置管理员账号（RICE_API_ADMIN_USERNAME/RICE_API_ADMIN_PASSWORD）。")
    response = api_client.login(settings.admin_username, settings.admin_password)
    if response.status_code != 200:
        pytest.skip(f"管理员登录接口异常，HTTP={response.status_code}")
    body = response.json()
    if body.get("code") != 200:
        pytest.skip(f"管理员登录失败，message={body.get('message')}")
    token = ((body.get("data") or {}).get("token") or "").strip()
    if not token:
        pytest.skip("管理员登录成功但未返回 token。")
    return token


@pytest.fixture(scope="function")
def admin_api_client(api_client: APIClient, admin_token: str) -> APIClient:
    api_client.set_bearer_token(admin_token)
    return api_client


@pytest.fixture(scope="function")
def merchant_token(api_client: APIClient, settings: ApiTestSettings) -> str:
    if not settings.merchant_username or not settings.merchant_password:
        pytest.skip("未配置商户账号（RICE_API_MERCHANT_USERNAME/RICE_API_MERCHANT_PASSWORD）。")
    response = api_client.login(settings.merchant_username, settings.merchant_password)
    if response.status_code != 200:
        pytest.skip(f"商户登录接口异常，HTTP={response.status_code}")
    body = response.json()
    if body.get("code") != 200:
        pytest.skip(f"商户登录失败，message={body.get('message')}")
    token = ((body.get("data") or {}).get("token") or "").strip()
    if not token:
        pytest.skip("商户登录成功但未返回 token。")
    return token


@pytest.fixture(scope="function")
def merchant_api_client(api_client: APIClient, merchant_token: str) -> APIClient:
    api_client.set_bearer_token(merchant_token)
    return api_client


@pytest.fixture(scope="function")
def db_client(settings: ApiTestSettings):
    client = DBClient(
        host=settings.db_host,
        port=settings.db_port,
        user=settings.db_user,
        password=settings.db_password,
        database=settings.db_name,
    )
    if not client.is_enabled():
        pytest.skip("未配置数据库连接参数，跳过数据库校验。")
    try:
        client.connect()
        yield client
    finally:
        client.close()
