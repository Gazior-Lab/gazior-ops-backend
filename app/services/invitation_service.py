import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums.common import WorkspaceMemberRole
from app.core.exceptions import DuplicateError, ForbiddenError, ObjectNotFoundError
from app.models.invitation import Invitation
from app.repositories.invitation import InvitationRepository
from app.repositories.user import UserRepository
from app.repositories.workspace import WorkspaceRepository
from app.repositories.workspace_member import WorkspaceMemberRepository
from app.schemas.invitation import InvitationCreate, InvitationCreatedResponse


class InvitationService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.invitation_repo = InvitationRepository(db)
        self.workspace_repo = WorkspaceRepository(db)
        self.member_repo = WorkspaceMemberRepository(db)
        self.user_repo = UserRepository(db)

    async def _require_admin_or_owner(self, workspace_id: int, current_user_id: int) -> None:
        member = await self.member_repo.get_by_user_and_workspace(
            user_id=current_user_id,
            workspace_id=workspace_id,
        )
        if not member or member.role not in (
            WorkspaceMemberRole.OWNER,
            WorkspaceMemberRole.ADMIN,
        ):
            raise ForbiddenError(
                message="You don't have permission to manage invitations",
            )

    async def list_invitations(
        self,
        workspace_id: int,
        current_user_id: int,
        skip: int = 0,
        limit: int = 100,
    ):
        workspace = await self.workspace_repo.get_by_id(workspace_id)
        if not workspace:
            raise ObjectNotFoundError(
                message=f"Workspace {workspace_id} not found",
                details={"workspace_id": workspace_id},
            )

        await self._require_admin_or_owner(workspace_id, current_user_id)

        invitations, total = await self.invitation_repo.get_by_workspace(
            workspace_id=workspace_id,
            skip=skip,
            limit=limit,
        )
        return {
            "invitations": invitations,
            "total": total,
            "skip": skip,
            "limit": limit,
        }

    async def create_invitation(
        self,
        workspace_id: int,
        data: InvitationCreate,
        current_user_id: int,
    ) -> InvitationCreatedResponse:
        workspace = await self.workspace_repo.get_by_id(workspace_id)
        if not workspace:
            raise ObjectNotFoundError(
                message=f"Workspace {workspace_id} not found",
                details={"workspace_id": workspace_id},
            )

        await self._require_admin_or_owner(workspace_id, current_user_id)

        email_normalized = data.email.lower()
        current_user = await self.user_repo.get_by_id(current_user_id)
        if current_user and current_user.email.lower() == email_normalized:
            raise DuplicateError(
                message="You cannot invite yourself",
                details={"email": data.email},
            )

        existing_user = await self.user_repo.get_by_email(email_normalized)
        if existing_user:
            member = await self.member_repo.get_by_user_and_workspace(
                user_id=existing_user.id,
                workspace_id=workspace_id,
            )
            if member:
                raise DuplicateError(
                    message="User is already a member of this workspace",
                    details={"email": data.email, "workspace_id": workspace_id},
                )

        pending = await self.invitation_repo.get_active_pending_for_email(
            workspace_id=workspace_id,
            email=email_normalized,
        )
        if pending:
            raise DuplicateError(
                message="An active invitation already exists for this email",
                details={"email": data.email, "workspace_id": workspace_id},
            )

        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(days=data.expires_in_days)
        token = secrets.token_urlsafe(32)

        invitation = Invitation(
            workspace_id=workspace_id,
            inviter_id=current_user_id,
            email=email_normalized,
            role=data.role,
            token=token,
            expires_at=expires_at,
            created_by_id=current_user_id,
            updated_by_id=current_user_id,
        )
        invitation = await self.invitation_repo.create(invitation)
        return InvitationCreatedResponse.model_validate(invitation)

    async def revoke_invitation(
        self,
        workspace_id: int,
        invitation_id: int,
        current_user_id: int,
    ) -> bool:
        workspace = await self.workspace_repo.get_by_id(workspace_id)
        if not workspace:
            raise ObjectNotFoundError(
                message=f"Workspace {workspace_id} not found",
                details={"workspace_id": workspace_id},
            )

        await self._require_admin_or_owner(workspace_id, current_user_id)

        invitation: Optional[Invitation] = await self.invitation_repo.get_by_id(
            invitation_id
        )
        if not invitation or invitation.workspace_id != workspace_id:
            raise ObjectNotFoundError(
                message="Invitation not found",
                details={"invitation_id": invitation_id, "workspace_id": workspace_id},
            )

        ok = await self.invitation_repo.revoke(invitation_id, current_user_id)
        if not ok:
            raise ObjectNotFoundError(
                message="Invitation not found",
                details={"invitation_id": invitation_id},
            )
        return True
