def _register_and_get_token(client, email="dave@example.com"):
    resp = client.post(
        "/api/v1/auth/register",
        json={"email": email, "full_name": "Dave", "password": "supersecret123"},
    )
    assert resp.status_code == 201
    return resp.json()["access_token"]


def test_send_message_creates_conversation(client):
    token = _register_and_get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.post(
        "/api/v1/chat/message",
        json={"message": "How much does the Pro plan cost?"},
        headers=headers,
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["conversation_id"]
    assert data["reply"]
    assert "product" in data["agents_used"] or "billing" in data["agents_used"]


def test_multi_agent_query_routes_to_both_agents(client):
    token = _register_and_get_token(client, email="eve@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.post(
        "/api/v1/chat/message",
        json={"message": "I paid yesterday, but my Premium account is still locked."},
        headers=headers,
    )
    assert resp.status_code == 200
    agents_used = resp.json()["agents_used"]
    assert "billing" in agents_used
    assert "technical" in agents_used


def test_conversation_memory_persists_across_messages(client):
    token = _register_and_get_token(client, email="frank@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    first = client.post(
        "/api/v1/chat/message",
        json={"message": "What features are included in the Premium plan?"},
        headers=headers,
    )
    conv_id = first.json()["conversation_id"]

    second = client.post(
        "/api/v1/chat/message",
        json={"message": "And what about support response time?", "conversation_id": conv_id},
        headers=headers,
    )
    assert second.json()["conversation_id"] == conv_id

    detail = client.get(f"/api/v1/chat/conversations/{conv_id}", headers=headers)
    assert detail.status_code == 200
    messages = detail.json()["messages"]
    # 2 user messages + 2 assistant replies = 4
    assert len(messages) == 4


def test_complaint_triggers_escalation(client):
    token = _register_and_get_token(client, email="grace@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.post(
        "/api/v1/chat/message",
        json={"message": "This is unacceptable, I want to cancel my subscription and speak to a manager"},
        headers=headers,
    )
    assert resp.status_code == 200
    assert resp.json()["escalated"] is True


def test_list_conversations_requires_auth(client):
    resp = client.get("/api/v1/chat/conversations")
    assert resp.status_code == 401


def test_health_check(client):
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
