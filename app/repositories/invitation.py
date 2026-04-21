from datetime import datetime, timezone
from typing import List, Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums.common import InvitationStatus
from app.models.invitation import Invitation


class InvitationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, invitation_id: int) -> Optional[Invitation]:
        result = await self.db.execute(
            select(Invitation).where(
                Invitation.id == invitation_id,
                Invitation.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def get_active_pending_for_email(
        self,
        workspace_id: int,
        email: str,
    ) -> Optional[Invitation]:
        now = datetime.now(timezone.utc)
        result = await self.db.execute(
            select(Invitation).where(
                Invitation.workspace_id == workspace_id,
                func.lower(Invitation.email) == email.lower(),
                Invitation.status == InvitationStatus.PENDING,
                Invitation.deleted_at.is_(None),
                Invitation.expires_at > now,
            )
        )
        return result.scalar_one_or_none()

    async def get_by_workspace(
        self,
        workspace_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> Tuple[List[Invitation], int]:
        query = select(Invitation).where(
            Invitation.workspace_id == workspace_id,
            Invitation.deleted_at.is_(None),
        )
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        query = query.order_by(Invitation.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all()), total

    async def create(self, invitation: Invitation) -> Invitation:
        self.db.add(invitation)
        await self.db.commit()
        await self.db.refresh(invitation)
        return invitation

    async def revoke(self, invitation_id: int, updated_by_id: int) -> bool:
        invitation = await self.get_by_id(invitation_id)
        if not invitation:
            return False
        invitation.status = InvitationStatus.REVOKED
        invitation.deleted_at = datetime.now(timezone.utc)
        invitation.updated_by_id = updated_by_id
        await self.db.commit()
        return True
