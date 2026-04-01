from sqlalchemy import String, DateTime, func, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column
from app.db.database import Base
from app.core.enums.common import ProjectStatus, ProjectVisibility


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    workspace_id: Mapped[int] = mapped_column(ForeignKey("workspaces.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    identifier: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    description: Mapped[str] = mapped_column(String(1000), nullable=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    status: Mapped[ProjectStatus] = mapped_column(Enum(ProjectStatus), nullable=False, default=ProjectStatus.PLANNED)
    visibility: Mapped[ProjectVisibility] = mapped_column(Enum(ProjectVisibility), nullable=False, default=ProjectVisibility.PRIVATE)
    status_changed_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=True)
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
