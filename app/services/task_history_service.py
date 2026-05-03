from typing import Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.task_history import TaskHistoryRepository
from app.repositories.task import TaskRepository
from app.repositories.workspace_member import WorkspaceMemberRepository
from app.core.exceptions import (
    ObjectNotFoundError,
    ForbiddenError,
)


class TaskHistoryService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.history_repo = TaskHistoryRepository(db)
        self.task_repo = TaskRepository(db)
        self.ws_member_repo = WorkspaceMemberRepository(db)

    async def _require_task_access(self, task_id: int, user_id: int) -> None:
        task = await self.task_repo.get_by_id(task_id)
        if not task:
            raise ObjectNotFoundError(
                message=f"Task {task_id} not found",
                details={"task_id": task_id},
            )
            
        ws_member = await self.ws_member_repo.get_by_user_and_workspace(
            user_id=user_id, workspace_id=task.workspace_id
        )
        if not ws_member:
            raise ForbiddenError(
                message="You don't have access to this task's workspace"
            )

    async def get_task_histories(
        self,
        task_id: int,
        current_user_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> Dict[str, Any]:
        await self._require_task_access(task_id, current_user_id)
        histories, total = await self.history_repo.get_all_by_task(
            task_id=task_id, skip=skip, limit=limit
        )
        return {"histories": histories, "total": total, "skip": skip, "limit": limit}
