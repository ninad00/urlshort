from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_healthz():
    r = client.get("/healthz")
    assert r.status_code == 200


def test_shorten_and_resolve():
    r = client.post("/shorten", json={"url": "https://example.com"})
    assert r.status_code == 201
    code = r.json()["code"]
    r = client.get(f"/{code}", follow_redirects=False)
    assert r.status_code == 307
    assert r.headers["location"] == "https://example.com/"


def test_unknown_code_returns_404():
    assert client.get("/nope").status_code == 404
