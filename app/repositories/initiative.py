from datetime import datetime, timezone
from typing import Optional, List, Tuple

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.initiative import Initiative


class InitiativeRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, initiative_id: int) -> Optional[Initiative]:
        """Get initiative by ID (excludes soft-deleted)."""
        result = await self.db.execute(
            select(Initiative).where(
                Initiative.id == initiative_id,
                Initiative.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def get_all_by_workspace(
        self,
        workspace_id: int,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        health_status: Optional[str] = None,
    ) -> Tuple[List[Initiative], int]:
        """Get initiatives for a workspace with optional search/status filter.
        Returns (initiatives, total_count).
        """
        query = select(Initiative).where(
            Initiative.workspace_id == workspace_id,
            Initiative.deleted_at.is_(None),
        )

        if search:
            query = query.where(
                Initiative.name.ilike(f"%{search}%")
            )

        if health_status:
            query = query.where(Initiative.health_status == health_status)

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        query = query.order_by(Initiative.created_at.desc()
                               ).offset(skip).limit(limit)
        result = await self.db.execute(query)
        initiatives = result.scalars().all()

        return initiatives, total

    async def create(self, initiative: Initiative) -> Initiative:
        """Persist a new Initiative instance."""
        self.db.add(initiative)
        await self.db.flush()
        await self.db.refresh(initiative)
        return initiative

    async def update(self, initiative_id: int, **kwargs) -> Optional[Initiative]:
        """Update initiative fields."""
        initiative = await self.get_by_id(initiative_id)
        if not initiative:
            return None

        for key, value in kwargs.items():
            if hasattr(initiative, key):
                setattr(initiative, key, value)

        await self.db.flush()
        await self.db.refresh(initiative)
        return initiative

    async def soft_delete(self, initiative_id: int, deleted_by_id: int) -> bool:
        """Soft-delete an initiative."""
        initiative = await self.get_by_id(initiative_id)
        if not initiative:
            return False

        initiative.deleted_at = datetime.now(timezone.utc)
        initiative.updated_by_id = deleted_by_id
        await self.db.flush()
        return True

    async def name_exists_in_workspace(
        self,
        name: str,
        workspace_id: int,
        exclude_id: Optional[int] = None,
    ) -> bool:
        """Check whether an initiative with the same name already exists in the workspace."""
        query = select(func.count(Initiative.id)).where(
            Initiative.name == name,
            Initiative.workspace_id == workspace_id,
            Initiative.deleted_at.is_(None),
        )
        if exclude_id:
            query = query.where(Initiative.id != exclude_id)

        result = await self.db.execute(query)
        return (result.scalar() or 0) > 0
