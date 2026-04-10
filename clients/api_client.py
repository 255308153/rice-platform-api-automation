from __future__ import annotations

from typing import Any

import requests


class APIClient:
    def __init__(self, base_url: str, timeout_seconds: int = 10):
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

    def set_bearer_token(self, token: str) -> None:
        self.session.headers["Authorization"] = f"Bearer {token}"

    def clear_bearer_token(self) -> None:
        self.session.headers.pop("Authorization", None)

    def request(self, method: str, path: str, **kwargs: Any) -> requests.Response:
        url = f"{self.base_url}/{path.lstrip('/')}"
        timeout = kwargs.pop("timeout", self.timeout_seconds)
        return self.session.request(method=method, url=url, timeout=timeout, **kwargs)

    def login(self, username: str, password: str) -> requests.Response:
        payload = {"username": username, "password": password}
        return self.request("POST", "/api/auth/login", json=payload)

    def close(self) -> None:
        self.session.close()

    def __enter__(self) -> "APIClient":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()
