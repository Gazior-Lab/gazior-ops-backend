from typing import Optional, List, Tuple

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.label import Label


class LabelRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, label_id: int) -> Optional[Label]:
        result = await self.db.execute(
            select(Label).where(
                Label.id == label_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_all_by_project(
        self,
        project_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> Tuple[List[Label], int]:
        query = select(Label).where(
            Label.project_id == project_id,
        )

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        query = query.order_by(Label.id.asc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        labels = result.scalars().all()

        return labels, total

    async def create(self, label: Label) -> Label:
        self.db.add(label)
        await self.db.flush()
        await self.db.refresh(label)
        return label

    async def update(self, label_id: int, **kwargs) -> Optional[Label]:
        label = await self.get_by_id(label_id)
        if not label:
            return None

        for key, value in kwargs.items():
            if hasattr(label, key):
                setattr(label, key, value)

        await self.db.flush()
        await self.db.refresh(label)
        return label

    async def delete(self, label_id: int) -> bool:
        label = await self.get_by_id(label_id)
        if not label:
            return False

        await self.db.delete(label)
        await self.db.flush()
        return True
