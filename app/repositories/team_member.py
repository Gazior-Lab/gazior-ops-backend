from datetime import datetime, timezone
from typing import Optional, List, Tuple

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.team_member import TeamMember
from app.core.enums.common import TeamMemberRole


class TeamMemberRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, member_id: int) -> Optional[TeamMember]:
        """Get team member by ID (excludes soft-deleted)"""
        result = await self.db.execute(
            select(TeamMember).where(
                TeamMember.id == member_id,
                TeamMember.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def get_by_user_and_team(
        self,
        user_id: int,
        team_id: int,
    ) -> Optional[TeamMember]:
        """Get a specific membership record"""
        result = await self.db.execute(
            select(TeamMember).where(
                TeamMember.user_id == user_id,
                TeamMember.team_id == team_id,
                TeamMember.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def get_by_team(
        self,
        team_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> Tuple[List[TeamMember], int]:
        """List all active members of a team with pagination.
        Returns (members, total_count).
        """
        query = select(TeamMember).where(
            TeamMember.team_id == team_id,
            TeamMember.deleted_at.is_(None),
        )

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        query = query.order_by(TeamMember.created_at.asc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        members = result.scalars().all()

        return members, total

    async def create(self, member: TeamMember) -> TeamMember:
        """Persist a new TeamMember"""
        self.db.add(member)
        await self.db.flush()
        await self.db.refresh(member)
        return member

    async def update_role(
        self,
        team_id: int,
        user_id: int,
        role: TeamMemberRole,
    ) -> Optional[TeamMember]:
        """Update a member's role within the team"""
        member = await self.get_by_user_and_team(user_id, team_id)
        if not member:
            return None

        member.role = role.value
        await self.db.flush()
        await self.db.refresh(member)
        return member

    async def soft_delete(self, member_id: int, deleted_by_id: int) -> bool:
        """Soft-delete a team membership"""
        member = await self.get_by_id(member_id)
        if not member:
            return False

        member.deleted_at = datetime.now(timezone.utc)
        member.updated_by_id = deleted_by_id
        await self.db.flush()
        return True
