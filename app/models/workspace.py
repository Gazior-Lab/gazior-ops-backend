from sqlalchemy import String, DateTime, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.db.database import Base



class Workspace(Base):
    __tablename__ = "workspaces"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    logo_url: Mapped[str] = mapped_column(String(255), nullable=True)
    timezone: Mapped[str] = mapped_column(String(50), default="UTC", nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=True)
    deleted_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=True)

    # server_default
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # foreign keys and relationships
    created_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)
    updated_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)