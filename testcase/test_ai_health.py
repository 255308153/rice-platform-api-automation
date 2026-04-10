def test_ai_chat_health_public_endpoint(api_client):
    response = api_client.request("GET", "/api/ai/chat/health")
    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 200
    assert body["message"] == "success"
    data = body["data"]
    assert isinstance(data, dict)
    assert "available" in data


def test_ai_recognition_health_public_endpoint(api_client):
    response = api_client.request("GET", "/api/ai/recognition/health")
    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 200
    assert body["message"] == "success"
    data = body["data"]
    assert isinstance(data, dict)
    assert "available" in data
