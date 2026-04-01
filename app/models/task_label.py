
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.db.database import Base


class TaskLabel(Base):
    __tablename__ = "task_labels"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"), index=True)
    label_id: Mapped[int] = mapped_column(ForeignKey("labels.id"), index=True) 