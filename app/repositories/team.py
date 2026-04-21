from datetime import datetime, timezone
from typing import Optional, List, Tuple

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.team import Team


class TeamRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, team_id: int) -> Optional[Team]:
        """Get team by ID (excludes soft-deleted)"""
        result = await self.db.execute(
            select(Team).where(
                Team.id == team_id,
                Team.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def get_all_by_workspace(
        self,
        workspace_id: int,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
    ) -> Tuple[List[Team], int]:
        """Get teams for a workspace with optional search.
        Returns (teams, total_count).
        """
        query = select(Team).where(
            Team.workspace_id == workspace_id,
            Team.deleted_at.is_(None),
        )

        if search:
            query = query.where(Team.name.ilike(f"%{search}%"))

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        query = query.order_by(Team.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        teams = result.scalars().all()

        return teams, total

    async def create(self, team: Team) -> Team:
        """Persist a new Team instance"""
        self.db.add(team)
        await self.db.commit()
        await self.db.refresh(team)
        return team

    async def update(self, team_id: int, **kwargs) -> Optional[Team]:
        """Update team fields"""
        team = await self.get_by_id(team_id)
        if not team:
            return None

        for key, value in kwargs.items():
            if hasattr(team, key):
                setattr(team, key, value)

        await self.db.commit()
        await self.db.refresh(team)
        return team

    async def soft_delete(self, team_id: int, deleted_by_id: int) -> bool:
        """Soft-delete a team"""
        team = await self.get_by_id(team_id)
        if not team:
            return False

        team.deleted_at = datetime.now(timezone.utc)
        team.updated_by_id = deleted_by_id
        await self.db.commit()
        return True

    async def name_exists_in_workspace(
        self,
        name: str,
        workspace_id: int,
        exclude_id: Optional[int] = None,
    ) -> bool:
        """Check whether a team with the same name already exists in the workspace"""
        query = select(func.count(Team.id)).where(
            Team.name == name,
            Team.workspace_id == workspace_id,
            Team.deleted_at.is_(None),
        )
        if exclude_id:
            query = query.where(Team.id != exclude_id)

        result = await self.db.execute(query)
        return (result.scalar() or 0) > 0
