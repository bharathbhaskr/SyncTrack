from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_db_check():
    r = client.get("/db-check")
    assert r.status_code == 200
    assert r.json()["db"] == "ok"