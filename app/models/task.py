from sqlalchemy import String, DateTime, Boolean, Integer, Float, ForeignKey, Enum, func
from sqlalchemy.orm import Mapped, mapped_column
from app.db.database import Base
from app.core.enums.common import TaskStatus, TaskPriority



class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    workspace_id: Mapped[int] = mapped_column(ForeignKey("workspaces.id"), nullable=False, index=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False, index=True)
    cycle_id: Mapped[int] = mapped_column(ForeignKey("cycles.id"), nullable=True, index=True)
    parent_task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"), nullable=True, index=True)
    
    number: Mapped[int] = mapped_column(Integer, nullable=False)
    identifier: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(2000), nullable=True)

    status: Mapped[TaskStatus] = mapped_column(Enum(TaskStatus), nullable=False, default=TaskStatus.BACKLOG)
    priority: Mapped[TaskPriority] = mapped_column(Enum(TaskPriority), nullable=False, default=TaskPriority.NONE)
    position: Mapped[int] = mapped_column(Integer, nullable=True)

    assignee_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    reporter_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    story_points: Mapped[float] = mapped_column(Float, nullable=True)
    due_date: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=True)
    ai_summary: Mapped[str] = mapped_column(String(2000), nullable=True)

    is_archived: Mapped[bool] = mapped_column(Boolean, default=False)
    archived_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=True)
    archived_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)

    status_changed_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=True)
    deleted_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=True)


    #server default timestamps
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

    # audit fields
    created_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)
    updated_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)