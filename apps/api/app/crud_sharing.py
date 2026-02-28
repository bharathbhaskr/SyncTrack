from sqlalchemy.orm import Session
from sqlalchemy import select, or_

from app.models import User, Checklist, ChecklistMember

def list_visible_checklists(db: Session, user_id: int) -> list[Checklist]:
    q = (
        select(Checklist)
        .join(ChecklistMember, ChecklistMember.checklist_id == Checklist.id)
        .where(ChecklistMember.user_id == user_id)
        .order_by(Checklist.id.desc())
    )
    return list(db.scalars(q).all())

def add_member_by_email(db: Session, checklist_id: int, email: str) -> ChecklistMember | None:
    user = db.scalar(select(User).where(User.email == email))
    if not user:
        return None

    # prevent duplicates
    existing = db.scalar(
        select(ChecklistMember).where(
            ChecklistMember.checklist_id == checklist_id,
            ChecklistMember.user_id == user.id,
        )
    )
    if existing:
        return existing

    member = ChecklistMember(checklist_id=checklist_id, user_id=user.id, role="member")
    db.add(member)
    db.commit()
    db.refresh(member)
    return member

def is_owner(db: Session, checklist_id: int, user_id: int) -> bool:
    q = select(Checklist).where(Checklist.id == checklist_id, Checklist.owner_id == user_id)
    return db.scalar(q) is not None