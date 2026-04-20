# app/services/task_service.py
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.task import TaskRepository
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate
from app.core.enums.common import TaskStatus, TaskPriority
class TaskService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.task_repo = TaskRepository(db)

    async def get_task(self, task_id: int) -> Optional[Task]:
        """Get a single task by ID"""
        return await self.task_repo.get_by_id(task_id)

    async def get_task_by_identifier(self, identifier: str) -> Optional[Task]:
        """Get task by identifier (e.g., GAZ-123)"""
        return await self.task_repo.get_by_identifier(identifier)

    async def get_tasks(
        self,
        skip: int = 0,
        limit: int = 100,
        workspace_id: Optional[int] = None,
        project_id: Optional[int] = None,
        cycle_id: Optional[int] = None,
        status: Optional[TaskStatus] = None,
        assignee_id: Optional[int] = None,
        priority: Optional[TaskPriority] = None,
        search: Optional[str] = None,
    ):
        """Get paginated tasks with filters"""
        tasks, total = await self.task_repo.get_all(
            skip=skip,
            limit=limit,
            workspace_id=workspace_id,
            project_id=project_id,
            cycle_id=cycle_id,
            status=status,
            assignee_id=assignee_id,
            priority=priority,
            search=search,
        )
        return {
            "tasks": tasks,
            "total": total,
            "skip": skip,
            "limit": limit
        }

    async def create_task(self, task_data: TaskCreate, current_user_id: int) -> Task:
        """Create a new task with business logic"""
        # Get next task number for the project
        next_number = await self.task_repo.get_next_task_number(task_data.project_id)
        
        # TODO: Fetch project identifier from Project repo
        # For now, using placeholder - you'll need to inject ProjectRepository
        project_identifier = "GAZ"  # This should come from project
        identifier = f"{project_identifier}-{next_number}"

        # Create task instance
        task = Task(
            **task_data.model_dump(),
            number=next_number,
            identifier=identifier,
            created_by_id=current_user_id,
            updated_by_id=current_user_id,
            status_changed_at=datetime.now(timezone.utc) if task_data.status else datetime.now(timezone.utc),
        )

        return await self.task_repo.create(task)

    async def update_task(
        self,
        task_id: int,
        task_data: TaskUpdate,
        current_user_id: int
    ) -> Optional[Task]:
        """Update task with business logic"""
        update_data = task_data.model_dump(exclude_unset=True)
        
        if not update_data:
            return await self.task_repo.get_by_id(task_id)

        # Add audit field
        update_data["updated_by_id"] = current_user_id

        return await self.task_repo.update(task_id, **update_data)

    async def delete_task(self, task_id: int, current_user_id: int) -> bool:
        """Soft delete a task"""
        return await self.task_repo.soft_delete(task_id, current_user_id)

    async def archive_task(self, task_id: int, current_user_id: int) -> Optional[Task]:
        """Archive a task"""
        return await self.task_repo.archive(task_id, current_user_id)

    async def unarchive_task(self, task_id: int, current_user_id: int) -> Optional[Task]:
        """Unarchive a task"""
        return await self.task_repo.unarchive(task_id, current_user_id)

    async def bulk_update_status(
        self,
        task_ids: List[int],
        status: TaskStatus,
        current_user_id: int
    ) -> int:
        """Bulk update task statuses"""
        return await self.task_repo.bulk_update_status(
            task_ids=task_ids,
            status=status,
            updated_by_id=current_user_id
        )

    async def get_task_metrics(self, project_id: int) -> Dict[str, Any]:
        """Get task metrics for a project (for dashboards)"""
        # This would typically use aggregate queries
        # For now, returning placeholder
        return {
            "total_tasks": 0,
            "completed_tasks": 0,
            "in_progress_tasks": 0,
            "overdue_tasks": 0,
        }
        
