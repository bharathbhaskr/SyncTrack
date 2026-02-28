from fastapi.testclient import TestClient
from sqlalchemy import text

from app.main import app
from app.db import SessionLocal

client = TestClient(app)

def _cleanup(email: str):
    db = SessionLocal()
    try:
        db.execute(text("DELETE FROM checklist_items"))
        db.execute(text("DELETE FROM checklist_members"))
        db.execute(text("DELETE FROM checklists"))
        db.execute(text("DELETE FROM users WHERE email = :email"), {"email": email})
        db.commit()
    finally:
        db.close()

def _signup_and_login(email: str, password: str) -> str:
    r = client.post("/auth/signup", json={"email": email, "password": password})
    assert r.status_code in (200, 409), r.text  # allow reruns

    r2 = client.post("/auth/login", json={"email": email, "password": password})
    assert r2.status_code == 200, r2.text
    return r2.json()["access_token"]

def test_create_checklist_add_item_toggle():
    email = "owner@example.com"
    password = "Passw0rd!"
    _cleanup(email)

    token = _signup_and_login(email, password)
    headers = {"Authorization": f"Bearer {token}"}

    # create checklist
    r = client.post("/checklists", json={"title": "Morning Routine"}, headers=headers)
    assert r.status_code == 200, r.text
    checklist_id = r.json()["id"]

    # add item
    r2 = client.post(f"/checklists/{checklist_id}/items", json={"text": "Chia water"}, headers=headers)
    assert r2.status_code == 200, r2.text
    item_id = r2.json()["id"]
    assert r2.json()["is_done"] is False

    # toggle
    r3 = client.patch(f"/items/{item_id}", headers=headers)
    assert r3.status_code == 200, r3.text
    assert r3.json()["is_done"] is True