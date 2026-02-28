from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, func, UniqueConstraint, ForeignKey, Boolean

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    __table_args__ = (UniqueConstraint("email", name="uq_users_email"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

# NEW MODELS (below User)
class Checklist(Base):
    __tablename__ = "checklists"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User")
    items = relationship("ChecklistItem", cascade="all, delete-orphan")
    members = relationship("ChecklistMember", cascade="all, delete-orphan")


class ChecklistItem(Base):
    __tablename__ = "checklist_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    checklist_id: Mapped[int] = mapped_column(ForeignKey("checklists.id"), nullable=False)
    text: Mapped[str] = mapped_column(String(300), nullable=False)
    is_done: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ChecklistMember(Base):
    __tablename__ = "checklist_members"
    __table_args__ = (UniqueConstraint("checklist_id", "user_id", name="uq_checklist_member"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    checklist_id: Mapped[int] = mapped_column(ForeignKey("checklists.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False, server_default="member")
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())