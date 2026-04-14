from datetime import datetime, timezone
from typing import Optional, List, Tuple

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.workspace_member import WorkspaceMember
from app.core.enums.common import WorkspaceMemberRole


class WorkspaceMemberRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, member_id: int) -> Optional[WorkspaceMember]:
        """Get workspace member by ID (excludes soft-deleted)"""
        result = await self.db.execute(
            select(WorkspaceMember).where(
                WorkspaceMember.id == member_id,
                WorkspaceMember.deleted_at.is_(None)
            )
        )
        return result.scalar_one_or_none()

    async def get_by_user_and_workspace(
        self,
        user_id: int,
        workspace_id: int,
    ) -> Optional[WorkspaceMember]:
        """Get workspace member by user_id and workspace_id"""
        result = await self.db.execute(
            select(WorkspaceMember).where(
                WorkspaceMember.user_id == user_id,
                WorkspaceMember.workspace_id == workspace_id,
                WorkspaceMember.deleted_at.is_(None)
            )
        )
        return result.scalar_one_or_none()

    async def get_by_workspace(
        self,
        workspace_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> Tuple[List[WorkspaceMember], int]:
        """Get all members of a workspace"""
        # Build base query
        query = select(WorkspaceMember).where(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.deleted_at.is_(None)
        )

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        # Apply pagination and ordering
        query = query.order_by(WorkspaceMember.joined_at.asc())
        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        members = result.scalars().all()

        return members, total

    async def get_owner_count(self, workspace_id: int) -> int:
        """Get count of owners in a workspace"""
        result = await self.db.execute(
            select(func.count(WorkspaceMember.id)).where(
                WorkspaceMember.workspace_id == workspace_id,
                WorkspaceMember.role == WorkspaceMemberRole.OWNER,
                WorkspaceMember.deleted_at.is_(None)
            )
        )
        return result.scalar() or 0

    async def create(self, member: WorkspaceMember) -> WorkspaceMember:
        """Create a new workspace member"""
        self.db.add(member)
        await self.db.commit()
        await self.db.refresh(member)
        return member

    async def update(self, member_id: int, **kwargs) -> Optional[WorkspaceMember]:
        """Update workspace member fields"""
        member = await self.get_by_id(member_id)
        if not member:
            return None

        for key, value in kwargs.items():
            if hasattr(member, key):
                setattr(member, key, value)

        await self.db.commit()
        await self.db.refresh(member)
        return member

    async def update_member_role(
        self,
        workspace_id: int,
        user_id: int,
        role: WorkspaceMemberRole,
    ) -> Optional[WorkspaceMember]:
        """Update a member's role"""
        member = await self.get_by_user_and_workspace(user_id, workspace_id)
        if not member:
            return None

        member.role = role
        await self.db.commit()
        await self.db.refresh(member)
        return member

    async def soft_delete(self, member_id: int, deleted_by_id: int) -> bool:
        """Soft delete a workspace member"""
        member = await self.get_by_id(member_id)
        if not member:
            return False

        member.deleted_at = datetime.now(timezone.utc)
        member.updated_by_id = deleted_by_id

        await self.db.commit()
        return True
