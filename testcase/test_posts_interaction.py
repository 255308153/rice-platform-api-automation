import pytest


def _get_first_post_id(authed_api_client):
    response = authed_api_client.request("GET", "/api/posts?page=1&size=1")
    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 200
    records = ((body.get("data") or {}).get("records") or [])
    if not records:
        pytest.skip("当前环境没有可交互帖子，跳过帖子交互测试。")
    post_id = records[0].get("id")
    assert post_id
    return post_id


@pytest.mark.auth
def test_favorite_list_success(authed_api_client):
    response = authed_api_client.request("GET", "/api/posts/favorites?page=1&size=5")
    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 200
    assert body["message"] == "success"
    data = body.get("data")
    assert isinstance(data, dict)
    assert isinstance(data.get("records"), list)


@pytest.mark.auth
def test_toggle_like_twice_restores_state(authed_api_client):
    post_id = _get_first_post_id(authed_api_client)

    first_resp = authed_api_client.request("POST", f"/api/posts/{post_id}/like")
    assert first_resp.status_code == 200
    first_body = first_resp.json()
    assert first_body["code"] == 200
    first_state = first_body.get("data")
    assert isinstance(first_state, bool)

    second_resp = authed_api_client.request("POST", f"/api/posts/{post_id}/like")
    assert second_resp.status_code == 200
    second_body = second_resp.json()
    assert second_body["code"] == 200
    second_state = second_body.get("data")
    assert isinstance(second_state, bool)
    assert second_state is (not first_state)


@pytest.mark.auth
def test_toggle_favorite_twice_restores_state(authed_api_client):
    post_id = _get_first_post_id(authed_api_client)

    first_resp = authed_api_client.request("POST", f"/api/posts/{post_id}/favorite")
    assert first_resp.status_code == 200
    first_body = first_resp.json()
    assert first_body["code"] == 200
    first_state = first_body.get("data")
    assert isinstance(first_state, bool)

    second_resp = authed_api_client.request("POST", f"/api/posts/{post_id}/favorite")
    assert second_resp.status_code == 200
    second_body = second_resp.json()
    assert second_body["code"] == 200
    second_state = second_body.get("data")
    assert isinstance(second_state, bool)
    assert second_state is (not first_state)


@pytest.mark.auth
def test_add_comment_empty_content_returns_business_error(authed_api_client):
    post_id = _get_first_post_id(authed_api_client)
    response = authed_api_client.request("POST", f"/api/posts/{post_id}/comment", json={"content": "   "})
    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 500
    assert "评论内容不能为空" in (body.get("message") or "")
