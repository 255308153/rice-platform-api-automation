import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


def _as_int(env_name: str, default: int) -> int:
    value = os.getenv(env_name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


@dataclass(frozen=True)
class ApiTestSettings:
    base_url: str
    timeout_seconds: int
    user_username: str
    user_password: str
    admin_username: str
    admin_password: str
    merchant_username: str
    merchant_password: str

    db_host: str
    db_port: int
    db_user: str
    db_password: str
    db_name: str


def load_settings() -> ApiTestSettings:
    return ApiTestSettings(
        base_url=os.getenv("RICE_API_BASE_URL", "http://localhost:8080").rstrip("/"),
        timeout_seconds=_as_int("RICE_API_TIMEOUT", 10),
        user_username=os.getenv("RICE_API_USER_USERNAME", ""),
        user_password=os.getenv("RICE_API_USER_PASSWORD", ""),
        admin_username=os.getenv("RICE_API_ADMIN_USERNAME", ""),
        admin_password=os.getenv("RICE_API_ADMIN_PASSWORD", ""),
        merchant_username=os.getenv("RICE_API_MERCHANT_USERNAME", ""),
        merchant_password=os.getenv("RICE_API_MERCHANT_PASSWORD", ""),
        db_host=os.getenv("RICE_DB_HOST", ""),
        db_port=_as_int("RICE_DB_PORT", 3306),
        db_user=os.getenv("RICE_DB_USER", ""),
        db_password=os.getenv("RICE_DB_PASSWORD", ""),
        db_name=os.getenv("RICE_DB_NAME", ""),
    )
