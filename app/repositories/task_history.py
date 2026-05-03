from typing import List, Tuple

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task_history import TaskHistory


class TaskHistoryRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_by_task(
        self,
        task_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> Tuple[List[TaskHistory], int]:
        query = select(TaskHistory).where(
            TaskHistory.task_id == task_id,
        )

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        query = query.order_by(TaskHistory.changed_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        histories = result.scalars().all()

        return histories, total

    async def create(self, history: TaskHistory) -> TaskHistory:
        self.db.add(history)
        await self.db.flush()
        await self.db.refresh(history)
        return history
