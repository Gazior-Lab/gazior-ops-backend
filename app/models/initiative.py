from sqlalchemy import String, DateTime, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.db.database import Base
from app.core.enums.common import InitiativeHealthStatus


class Initiative(Base):
    __tablename__ = "initiatives"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    workspace_id: Mapped[int] = mapped_column(ForeignKey("workspaces.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    summary: Mapped[str] = mapped_column(String(1000), nullable=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    health_status: Mapped[InitiativeHealthStatus] = mapped_column(nullable=False, default=InitiativeHealthStatus.ON_TRACK)
    progress_percentage: Mapped[int] = mapped_column(nullable=False, default=0)
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
