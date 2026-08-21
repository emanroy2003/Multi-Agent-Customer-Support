def test_register_and_login(client):
    resp = client.post(
        "/api/v1/auth/register",
        json={"email": "alice@example.com", "full_name": "Alice Test", "password": "supersecret123"},
    )
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["user"]["email"] == "alice@example.com"
    assert "access_token" in data

    resp = client.post(
        "/api/v1/auth/login", json={"email": "alice@example.com", "password": "supersecret123"}
    )
    assert resp.status_code == 200
    token = resp.json()["access_token"]

    resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["email"] == "alice@example.com"


def test_duplicate_registration_rejected(client):
    payload = {"email": "bob@example.com", "full_name": "Bob", "password": "supersecret123"}
    resp1 = client.post("/api/v1/auth/register", json=payload)
    assert resp1.status_code == 201

    resp2 = client.post("/api/v1/auth/register", json=payload)
    assert resp2.status_code == 400


def test_login_wrong_password_rejected(client):
    client.post(
        "/api/v1/auth/register",
        json={"email": "carol@example.com", "full_name": "Carol", "password": "correctpassword"},
    )
    resp = client.post(
        "/api/v1/auth/login", json={"email": "carol@example.com", "password": "wrongpassword"}
    )
    assert resp.status_code == 401


def test_protected_route_requires_token(client):
    resp = client.get("/api/v1/auth/me")
    assert resp.status_code == 401
