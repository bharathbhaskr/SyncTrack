from fastapi.testclient import TestClient
from sqlalchemy import text

from app.main import app
from app.db import SessionLocal

client = TestClient(app)

def _wipe_all():
    db = SessionLocal()
    try:
        db.execute(text("DELETE FROM checklist_items"))
        db.execute(text("DELETE FROM checklist_members"))
        db.execute(text("DELETE FROM checklists"))
        db.execute(text("DELETE FROM users"))
        db.commit()
    finally:
        db.close()

def _signup_and_login(email: str, password: str) -> str:
    r = client.post("/auth/signup", json={"email": email, "password": password})
    assert r.status_code in (200, 409), r.text
    r2 = client.post("/auth/login", json={"email": email, "password": password})
    assert r2.status_code == 200, r2.text
    return r2.json()["access_token"]

def test_share_checklist_and_access():
    _wipe_all()

    owner_email = "owner2@example.com"
    friend_email = "friend@example.com"
    pw = "Passw0rd!"

    owner_token = _signup_and_login(owner_email, pw)
    friend_token = _signup_and_login(friend_email, pw)

    owner_headers = {"Authorization": f"Bearer {owner_token}"}
    friend_headers = {"Authorization": f"Bearer {friend_token}"}

    # owner creates checklist
    r = client.post("/checklists", json={"title": "Shared List"}, headers=owner_headers)
    assert r.status_code == 200, r.text
    checklist_id = r.json()["id"]

    # share with friend
    r2 = client.post(f"/checklists/{checklist_id}/share", json={"email": friend_email}, headers=owner_headers)
    assert r2.status_code == 200, r2.text

    # friend can list it
    r3 = client.get("/checklists", headers=friend_headers)
    assert r3.status_code == 200, r3.text
    ids = [c["id"] for c in r3.json()]
    assert checklist_id in ids

    # friend can add item
    r4 = client.post(f"/checklists/{checklist_id}/items", json={"text": "Do it together"}, headers=friend_headers)
    assert r4.status_code == 200, r4.text