from sqlalchemy import String, Enum, DateTime, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.db.database import Base
from app.core.enums.common import InvitationStatus, WorkspaceMemberRole


class Invitation(Base):
    __tablename__ = "invitations"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    workspace_id: Mapped[int] = mapped_column(ForeignKey("workspaces.id"), nullable=False, index=True)
    inviter_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    role: Mapped[WorkspaceMemberRole] = mapped_column(Enum(WorkspaceMemberRole), nullable=False)
    token: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    status: Mapped[InvitationStatus] = mapped_column(Enum(InvitationStatus), default=InvitationStatus.PENDING, nullable=False)
    expires_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)
    accepted_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=True)
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