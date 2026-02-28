from fastapi.testclient import TestClient
from sqlalchemy import text

from app.main import app
from app.db import SessionLocal

client = TestClient(app)

def _cleanup_user(email: str) -> None:
    # Ensures the test is repeatable even if run multiple times
    db = SessionLocal()
    try:
        db.execute(text("DELETE FROM users WHERE email = :email"), {"email": email})
        db.commit()
    finally:
        db.close()

def test_signup_and_login():
    email = "test@example.com"
    password = "Passw0rd!"

    _cleanup_user(email)

    # signup
    r = client.post("/auth/signup", json={"email": email, "password": password})
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["email"] == email
    assert "id" in data

    # duplicate signup
    r2 = client.post("/auth/signup", json={"email": email, "password": password})
    assert r2.status_code == 409

    # login
    r3 = client.post("/auth/login", json={"email": email, "password": password})
    assert r3.status_code == 200, r3.text
    token_data = r3.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"