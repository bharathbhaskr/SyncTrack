from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models import Checklist, ChecklistItem, ChecklistMember, User

def create_checklist(db: Session, owner: User, title: str) -> Checklist:
    cl = Checklist(owner_id=owner.id, title=title)
    db.add(cl)
    db.commit()
    db.refresh(cl)

    # owner is implicitly a member too
    db.add(ChecklistMember(checklist_id=cl.id, user_id=owner.id, role="owner"))
    db.commit()
    return cl

def add_item(db: Session, checklist_id: int, text: str) -> ChecklistItem:
    item = ChecklistItem(checklist_id=checklist_id, text=text)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

def toggle_item(db: Session, item_id: int) -> ChecklistItem | None:
    item = db.get(ChecklistItem, item_id)
    if not item:
        return None
    item.is_done = not item.is_done
    db.commit()
    db.refresh(item)
    return item

def is_member(db: Session, checklist_id: int, user_id: int) -> bool:
    q = select(ChecklistMember).where(
        ChecklistMember.checklist_id == checklist_id,
        ChecklistMember.user_id == user_id,
    )
    return db.scalar(q) is not None