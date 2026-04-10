import pytest


@pytest.mark.auth
def test_admin_update_user_status_roundtrip(admin_api_client):
    me_resp = admin_api_client.request("GET", "/api/user/info")
    assert me_resp.status_code == 200
    me_body = me_resp.json()
    assert me_body["code"] == 200
    admin_id = ((me_body.get("data") or {}).get("id"))
    assert admin_id

    list_resp = admin_api_client.request("GET", "/api/admin/users?page=1&size=30")
    assert list_resp.status_code == 200
    list_body = list_resp.json()
    assert list_body["code"] == 200
    records = ((list_body.get("data") or {}).get("records") or [])
    target = next(
        (
            user
            for user in records
            if str(user.get("role", "")).upper() != "ADMIN" and int(user.get("id", 0)) != int(admin_id)
        ),
        None,
    )
    if target is None:
        pytest.skip("当前环境未找到可修改状态的非管理员用户。")

    user_id = target.get("id")
    old_status = target.get("status")
    assert user_id is not None and old_status in (0, 1)
    new_status = 0 if int(old_status) == 1 else 1

    try:
        update_resp = admin_api_client.request(
            "PUT",
            f"/api/admin/users/{user_id}/status",
            json={"status": new_status},
        )
        assert update_resp.status_code == 200
        update_body = update_resp.json()
        assert update_body["code"] == 200
        assert update_body["message"] == "success"
    finally:
        restore_resp = admin_api_client.request(
            "PUT",
            f"/api/admin/users/{user_id}/status",
            json={"status": int(old_status)},
        )
        assert restore_resp.status_code == 200
        restore_body = restore_resp.json()
        assert restore_body["code"] == 200


@pytest.mark.auth
def test_admin_update_post_status_roundtrip(admin_api_client):
    list_resp = admin_api_client.request("GET", "/api/admin/content/posts?page=1&size=20&status=-1")
    assert list_resp.status_code == 200
    list_body = list_resp.json()
    assert list_body["code"] == 200
    records = ((list_body.get("data") or {}).get("records") or [])
    if not records:
        pytest.skip("当前环境无帖子可用于状态修改测试。")

    post = records[0]
    post_id = post.get("id")
    old_status = post.get("status")
    if post_id is None or old_status not in (0, 1, 2):
        pytest.skip("帖子数据缺少必要字段，跳过状态修改测试。")

    new_status = 2 if int(old_status) != 2 else 1

    try:
        update_resp = admin_api_client.request(
            "PUT",
            f"/api/admin/content/posts/{post_id}/status",
            json={"status": new_status, "remark": "自动化测试状态切换"},
        )
        assert update_resp.status_code == 200
        update_body = update_resp.json()
        assert update_body["code"] == 200
        assert update_body["message"] == "success"
    finally:
        restore_resp = admin_api_client.request(
            "PUT",
            f"/api/admin/content/posts/{post_id}/status",
            json={"status": int(old_status), "remark": "自动化恢复原状态"},
        )
        assert restore_resp.status_code == 200
        restore_body = restore_resp.json()
        assert restore_body["code"] == 200


@pytest.mark.auth
def test_admin_update_comment_status_roundtrip(admin_api_client):
    list_resp = admin_api_client.request("GET", "/api/admin/content/comments?page=1&size=20&status=-1")
    assert list_resp.status_code == 200
    list_body = list_resp.json()
    assert list_body["code"] == 200
    records = ((list_body.get("data") or {}).get("records") or [])
    if not records:
        pytest.skip("当前环境无评论可用于状态修改测试。")

    comment = records[0]
    comment_id = comment.get("id")
    old_status = comment.get("status")
    if comment_id is None or old_status not in (0, 1):
        pytest.skip("评论数据缺少必要字段，跳过状态修改测试。")

    new_status = 0 if int(old_status) == 1 else 1

    try:
        update_resp = admin_api_client.request(
            "PUT",
            f"/api/admin/content/comments/{comment_id}/status",
            json={"status": new_status, "remark": "自动化测试状态切换"},
        )
        assert update_resp.status_code == 200
        update_body = update_resp.json()
        assert update_body["code"] == 200
        assert update_body["message"] == "success"
    finally:
        restore_resp = admin_api_client.request(
            "PUT",
            f"/api/admin/content/comments/{comment_id}/status",
            json={"status": int(old_status), "remark": "自动化恢复原状态"},
        )
        assert restore_resp.status_code == 200
        restore_body = restore_resp.json()
        assert restore_body["code"] == 200

