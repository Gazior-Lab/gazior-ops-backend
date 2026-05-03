from typing import Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.task_label import TaskLabelRepository
from app.repositories.task import TaskRepository
from app.repositories.label import LabelRepository
from app.repositories.workspace_member import WorkspaceMemberRepository
from app.models.task_label import TaskLabel
from app.schemas.task_label import TaskLabelCreate
from app.core.exceptions import (
    ObjectNotFoundError,
    ForbiddenError,
    DuplicateError,
)


class TaskLabelService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.task_label_repo = TaskLabelRepository(db)
        self.task_repo = TaskRepository(db)
        self.label_repo = LabelRepository(db)
        self.ws_member_repo = WorkspaceMemberRepository(db)

    async def _require_task_access(self, task_id: int, user_id: int) -> int:
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
        return task.project_id

    async def get_task_labels(
        self,
        task_id: int,
        current_user_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> Dict[str, Any]:
        await self._require_task_access(task_id, current_user_id)
        task_labels, total = await self.task_label_repo.get_all_by_task(
            task_id=task_id, skip=skip, limit=limit
        )
        return {"task_labels": task_labels, "total": total, "skip": skip, "limit": limit}

    async def add_label_to_task(
        self,
        task_label_data: TaskLabelCreate,
        current_user_id: int,
    ) -> TaskLabel:
        project_id = await self._require_task_access(task_label_data.task_id, current_user_id)

        label = await self.label_repo.get_by_id(task_label_data.label_id)
        if not label or label.project_id != project_id:
            raise ObjectNotFoundError(
                message=f"Label {task_label_data.label_id} not found in this project",
            )
            
        existing = await self.task_label_repo.get_by_task_and_label(
            task_id=task_label_data.task_id, label_id=task_label_data.label_id
        )
        if existing:
            raise DuplicateError(message="Task already has this label")

        task_label = TaskLabel(
            task_id=task_label_data.task_id,
            label_id=task_label_data.label_id,
        )
        return await self.task_label_repo.create(task_label)

    async def remove_label_from_task(
        self,
        task_id: int,
        label_id: int,
        current_user_id: int,
    ) -> bool:
        await self._require_task_access(task_id, current_user_id)

        existing = await self.task_label_repo.get_by_task_and_label(
            task_id=task_id, label_id=label_id
        )
        if not existing:
            raise ObjectNotFoundError(message="Task does not have this label")

        return await self.task_label_repo.delete(existing.id)
