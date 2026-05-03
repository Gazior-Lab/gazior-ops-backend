from typing import List, Tuple

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task_label import TaskLabel


class TaskLabelRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_task_and_label(self, task_id: int, label_id: int) -> TaskLabel | None:
        result = await self.db.execute(
            select(TaskLabel).where(
                and_(
                    TaskLabel.task_id == task_id,
                    TaskLabel.label_id == label_id
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_all_by_task(
        self,
        task_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> Tuple[List[TaskLabel], int]:
        query = select(TaskLabel).where(
            TaskLabel.task_id == task_id,
        )

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        query = query.order_by(TaskLabel.id.asc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        task_labels = result.scalars().all()

        return task_labels, total

    async def create(self, task_label: TaskLabel) -> TaskLabel:
        self.db.add(task_label)
        await self.db.flush()
        await self.db.refresh(task_label)
        return task_label

    async def delete(self, task_label_id: int) -> bool:
        result = await self.db.execute(
            select(TaskLabel).where(TaskLabel.id == task_label_id)
        )
        task_label = result.scalar_one_or_none()
        
        if not task_label:
            return False

        await self.db.delete(task_label)
        await self.db.flush()
        return True
