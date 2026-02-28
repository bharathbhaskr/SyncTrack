from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel, EmailStr
from app.models import ChecklistItem
from app.auth import get_current_user
from app.crud_checklists import create_checklist, add_item, toggle_item, is_member
from app.models import User
from app.crud_sharing import add_member_by_email, list_visible_checklists, is_owner
from app.db import get_db
from app.security import hash_password, verify_password, create_access_token
from app.crud_users import get_user_by_email, create_user

app = FastAPI(title="BuddyCheck API")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/db-check")
def db_check(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"db": "ok"}

class SignupIn(BaseModel):
    email: EmailStr
    password: str

class LoginIn(BaseModel):
    email: EmailStr
    password: str

@app.post("/auth/signup")
def signup(payload: SignupIn, db: Session = Depends(get_db)):
    existing = get_user_by_email(db, payload.email)
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    user = create_user(db, payload.email, hash_password(payload.password))
    return {"id": user.id, "email": user.email}

@app.post("/auth/login")
def login(payload: LoginIn, db: Session = Depends(get_db)):
    user = get_user_by_email(db, payload.email)
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(subject=str(user.id))
    return {"access_token": token, "token_type": "bearer"}

class ChecklistCreateIn(BaseModel):
    title: str

class ItemCreateIn(BaseModel):
    text: str

@app.post("/checklists")
def create_checklist_route(payload: ChecklistCreateIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    cl = create_checklist(db, owner=user, title=payload.title)
    return {"id": cl.id, "title": cl.title}

@app.post("/checklists/{checklist_id}/items")
def add_item_route(checklist_id: int, payload: ItemCreateIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if not is_member(db, checklist_id, user.id):
        raise HTTPException(status_code=403, detail="Not a member of this checklist")
    item = add_item(db, checklist_id=checklist_id, text=payload.text)
    return {"id": item.id, "text": item.text, "is_done": item.is_done}

@app.patch("/items/{item_id}")
def toggle_item_route(item_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    item = db.get(ChecklistItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not is_member(db, item.checklist_id, user.id):
        raise HTTPException(status_code=403, detail="Not a member of this checklist")

    updated = toggle_item(db, item_id=item_id)
    return {"id": updated.id, "is_done": updated.is_done}

class ShareIn(BaseModel):
    email: EmailStr

@app.get("/checklists")
def list_checklists(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    checklists = list_visible_checklists(db, user.id)
    return [{"id": c.id, "title": c.title, "owner_id": c.owner_id} for c in checklists]

@app.post("/checklists/{checklist_id}/share")
def share_checklist(checklist_id: int, payload: ShareIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if not is_owner(db, checklist_id, user.id):
        raise HTTPException(status_code=403, detail="Only owner can share")

    member = add_member_by_email(db, checklist_id, payload.email)
    if not member:
        raise HTTPException(status_code=404, detail="User not found")

    return {"checklist_id": checklist_id, "shared_with": payload.email}