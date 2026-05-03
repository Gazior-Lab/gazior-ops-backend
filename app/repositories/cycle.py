from datetime import datetime, timezone
from typing import Optional, List, Tuple

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cycle import Cycle


class CycleRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, cycle_id: int) -> Optional[Cycle]:
        result = await self.db.execute(
            select(Cycle).where(
                Cycle.id == cycle_id,
                Cycle.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def get_all_by_project(
        self,
        project_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> Tuple[List[Cycle], int]:
        query = select(Cycle).where(
            Cycle.project_id == project_id,
            Cycle.deleted_at.is_(None),
        )

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        query = query.order_by(Cycle.created_at.desc()
                               ).offset(skip).limit(limit)
        result = await self.db.execute(query)
        cycles = result.scalars().all()

        return cycles, total

    async def create(self, cycle: Cycle) -> Cycle:
        self.db.add(cycle)
        await self.db.flush()
        await self.db.refresh(cycle)
        return cycle

    async def update(self, cycle_id: int, **kwargs) -> Optional[Cycle]:
        cycle = await self.get_by_id(cycle_id)
        if not cycle:
            return None

        for key, value in kwargs.items():
            if hasattr(cycle, key):
                setattr(cycle, key, value)

        await self.db.flush()
        await self.db.refresh(cycle)
        return cycle

    async def soft_delete(self, cycle_id: int, deleted_by_id: int) -> bool:
        cycle = await self.get_by_id(cycle_id)
        if not cycle:
            return False

        cycle.deleted_at = datetime.now(timezone.utc)
        cycle.updated_by_id = deleted_by_id
        await self.db.flush()
        return True
