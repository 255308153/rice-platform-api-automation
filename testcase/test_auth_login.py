import pytest
from utils import load_yaml_cases, validate_with_schema


@pytest.mark.smoke
@pytest.mark.auth
def test_user_login_success_returns_token(api_client, settings):
    if not settings.user_username or not settings.user_password:
        pytest.skip("未配置登录账号（RICE_API_USER_USERNAME/RICE_API_USER_PASSWORD）。")

    response = api_client.login(settings.user_username, settings.user_password)
    assert response.status_code == 200

    body = response.json()
    validate_with_schema(body, "auth_login_success.json")

    assert body["code"] == 200
    assert body["message"] == "success"
    token = body["data"]["token"]
    assert token
    assert token.count(".") == 2


@pytest.mark.auth
@pytest.mark.parametrize(
    "case_data",
    load_yaml_cases("auth_login_cases.yaml"),
    ids=lambda item: item["case_name"],
)
def test_user_login_invalid_credentials_returns_business_error(api_client, case_data):
    response = api_client.login(case_data["username"], case_data["password"])
    assert response.status_code == 200

    body = response.json()
    assert body["code"] == case_data["expected_code"]
    assert case_data["expected_message_contains"] in (body.get("message") or "")
