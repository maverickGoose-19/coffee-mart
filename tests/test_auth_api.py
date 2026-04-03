from __future__ import annotations

from fastapi.testclient import TestClient

from product.backend.app import main


def test_signin_sets_session_cookie(monkeypatch):
    monkeypatch.setattr(main, "ensure_demo_data", lambda: None)
    monkeypatch.setattr(
        main,
        "sign_in",
        lambda payload: (
            {
                "id": "user_001",
                "email": payload.email,
                "role": "buyer",
                "buyer_id": "buyer_001",
                "display_name": "Harborline",
            },
            "token_123",
        ),
    )

    with TestClient(main.app) as client:
        response = client.post(
            "/api/auth/signin",
            json={"email": "buyer@example.com", "password": "Password123!"},
        )

    assert response.status_code == 200
    assert response.json()["currentUser"]["role"] == "buyer"
    assert response.cookies.get("coffee_session") == "token_123"


def test_signin_surfaces_structured_error(monkeypatch):
    monkeypatch.setattr(main, "ensure_demo_data", lambda: None)

    with TestClient(main.app) as client:
        response = client.post(
            "/api/auth/signin",
            json={"email": "buyer@example.com"},
        )

    assert response.status_code == 422
    assert "error" in response.json()
