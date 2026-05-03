from typing import Optional, List, Tuple

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.update import Update


class UpdateRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, update_id: int) -> Optional[Update]:
        """Get update by ID."""
        result = await self.db.execute(
            select(Update).where(
                Update.id == update_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_all_by_workspace(
        self,
        workspace_id: int,
        skip: int = 0,
        limit: int = 100,
        tag: Optional[str] = None,
        department: Optional[str] = None,
    ) -> Tuple[List[Update], int]:
        """Get updates for a workspace. Returns (updates, total_count)."""
        query = select(Update).where(
            Update.workspace_id == workspace_id,
        )

        if tag:
            query = query.where(Update.tag == tag)
        if department:
            query = query.where(Update.department == department)

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        query = query.order_by(Update.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        updates = result.scalars().all()

        return updates, total

    async def create(self, update: Update) -> Update:
        """Persist a new Update instance."""
        self.db.add(update)
        await self.db.flush()
        await self.db.refresh(update)
        return update

    async def update(self, update_id: int, **kwargs) -> Optional[Update]:
        """Update fields for an Update."""
        update_obj = await self.get_by_id(update_id)
        if not update_obj:
            return None

        for key, value in kwargs.items():
            if hasattr(update_obj, key):
                setattr(update_obj, key, value)

        await self.db.flush()
        await self.db.refresh(update_obj)
        return update_obj

    async def delete(self, update_id: int) -> bool:
        """Hard-delete an update (Update model has no soft-delete fields)."""
        update_obj = await self.get_by_id(update_id)
        if not update_obj:
            return False

        await self.db.delete(update_obj)
        await self.db.flush()
        return True
