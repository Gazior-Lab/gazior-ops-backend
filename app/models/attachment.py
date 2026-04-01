from sqlalchemy import String, DateTime, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.db.database import Base



class Attachment(Base):
    __tablename__ = "attachments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"), nullable=False, index=True)
    uploader_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)

    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(255), nullable=False)
    size_bytes: Mapped[int] = mapped_column(nullable=False)

    deleted_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=True)

    # Server default timestamps
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

    # Audit fields
    created_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)
    updated_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)