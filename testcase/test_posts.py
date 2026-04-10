import pytest


@pytest.mark.auth
def test_post_categories_success(authed_api_client):
    response = authed_api_client.request("GET", "/api/posts/categories")
    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 200
    assert body["message"] == "success"
    assert isinstance(body.get("data"), list)


@pytest.mark.smoke
def test_post_list_success(authed_api_client):
    response = authed_api_client.request("GET", "/api/posts?page=1&size=5")
    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 200
    assert body["message"] == "success"
    data = body["data"]
    assert isinstance(data, dict)
    assert isinstance(data.get("records"), list)
    assert int(data.get("size", 0)) == 5


@pytest.mark.auth
def test_my_posts_success(authed_api_client):
    response = authed_api_client.request("GET", "/api/posts/my?page=1&size=5")
    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 200
    assert body["message"] == "success"
    data = body["data"]
    assert isinstance(data, dict)
    assert isinstance(data.get("records"), list)
