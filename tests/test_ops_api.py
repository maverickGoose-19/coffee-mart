from __future__ import annotations

from fastapi.testclient import TestClient

from product.backend.app import main


def test_healthz_reports_service_metadata(monkeypatch):
    monkeypatch.setattr(main, "ensure_demo_data", lambda: None)
    with TestClient(main.app) as client:
        response = client.get("/healthz")
    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True
    assert "service" in payload
    assert "version" in payload


def test_readyz_uses_database_probe(monkeypatch):
    monkeypatch.setattr(main, "ensure_demo_data", lambda: None)
    monkeypatch.setattr(main._db, "query_one", lambda sql: {"ok": 1})
    with TestClient(main.app) as client:
        response = client.get("/readyz")
    assert response.status_code == 200
    assert response.json()["database"] is True
