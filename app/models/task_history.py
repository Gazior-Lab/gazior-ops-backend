from sqlalchemy import String, DateTime, func, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column
from app.db.database import Base


class TaskHistory(Base):
    __tablename__ = "task_histories"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"), nullable=False, index=True)
    field_name: Mapped[str] = mapped_column(String(255), nullable=False)

    old_value: Mapped[str] = mapped_column(String(1000), nullable=True)
    new_value: Mapped[str] = mapped_column(String(1000), nullable=True)

    changed_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    changed_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)