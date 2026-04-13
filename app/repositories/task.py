# app/repositories/task.py
from uuid import UUID
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task
from app.core.enums.common import TaskStatus, TaskPriority


class TaskRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, task_id: UUID) -> Optional[Task]:
        """Get task by ID (excludes soft-deleted)"""
        result = await self.db.execute(
            select(Task).where(
                Task.id == task_id,
                Task.deleted_at.is_(None)
            )
        )
        return result.scalar_one_or_none()

    async def get_by_identifier(self, identifier: str) -> Optional[Task]:
        """Get task by identifier (e.g., GAZ-123)"""
        result = await self.db.execute(
            select(Task).where(
                Task.identifier == identifier,
                Task.deleted_at.is_(None)
            )
        )
        return result.scalar_one_or_none()

    async def get_next_task_number(self, project_id: UUID) -> int:
        """Get next sequential task number for a project"""
        result = await self.db.execute(
            select(func.max(Task.number)).where(
                Task.project_id == project_id,
                Task.deleted_at.is_(None)
            )
        )
        max_number = result.scalar()
        return (max_number or 0) + 1

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        workspace_id: Optional[UUID] = None,
        project_id: Optional[UUID] = None,
        cycle_id: Optional[UUID] = None,
        status: Optional[TaskStatus] = None,
        assignee_id: Optional[UUID] = None,
        priority: Optional[TaskPriority] = None,
        search: Optional[str] = None,
    ) -> tuple[List[Task], int]:
        """
        Get tasks with filtering, sorting, and pagination.
        Returns (tasks, total_count)
        """
        # Build base query
        query = select(Task).where(Task.deleted_at.is_(None))

        # Apply filters
        if workspace_id:
            query = query.where(Task.workspace_id == workspace_id)
        if project_id:
            query = query.where(Task.project_id == project_id)
        if cycle_id is not None:  # Allow None to filter tasks without cycle
            query = query.where(Task.cycle_id == cycle_id)
        if status:
            query = query.where(Task.status == status)
        if assignee_id is not None:  # Allow None to filter unassigned
            query = query.where(Task.assignee_id == assignee_id)
        if priority:
            query = query.where(Task.priority == priority)
        if search:
            query = query.where(
                or_(
                    Task.title.ilike(f"%{search}%"),
                    Task.identifier.ilike(f"%{search}%"),
                    Task.description.ilike(f"%{search}%")
                )
            )

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        # Apply pagination and ordering
        query = query.order_by(Task.position.asc(), Task.created_at.desc())
        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        tasks = result.scalars().all()

        return tasks, total

    async def create(self, task: Task) -> Task:
        """Create a new task"""
        self.db.add(task)
        await self.db.commit()
        await self.db.refresh(task)
        return task

    async def update(self, task_id: UUID, **kwargs) -> Optional[Task]:
        """Update task fields"""
        task = await self.get_by_id(task_id)
        if not task:
            return None

        # Handle status change timestamp
        if "status" in kwargs and kwargs["status"] != task.status:
            kwargs["status_changed_at"] = datetime.now(timezone.utc)

        for key, value in kwargs.items():
            if hasattr(task, key):
                setattr(task, key, value)

        await self.db.commit()
        await self.db.refresh(task)
        return task

    async def soft_delete(self, task_id: UUID, deleted_by_id: UUID) -> bool:
        """Soft delete a task"""
        task = await self.get_by_id(task_id)
        if not task:
            return False

        task.deleted_at = datetime.now(timezone.utc)
        task.updated_by_id = deleted_by_id

        await self.db.commit()
        return True

    async def hard_delete(self, task_id: UUID) -> bool:
        """Permanently delete a task (admin only)"""
        task = await self.get_by_id(task_id)
        if not task:
            return False

        await self.db.delete(task)
        await self.db.commit()
        return True

    async def archive(self, task_id: UUID, archived_by_id: UUID) -> Optional[Task]:
        """Archive a task"""
        task = await self.get_by_id(task_id)
        if not task:
            return None

        task.is_archived = True
        task.archived_at = datetime.now(timezone.utc)
        task.archived_by_id = archived_by_id
        task.updated_by_id = archived_by_id

        await self.db.commit()
        await self.db.refresh(task)
        return task

    async def unarchive(self, task_id: UUID, updated_by_id: UUID) -> Optional[Task]:
        """Unarchive a task"""
        task = await self.get_by_id(task_id)
        if not task:
            return None

        task.is_archived = False
        task.archived_at = None
        task.archived_by_id = None
        task.updated_by_id = updated_by_id

        await self.db.commit()
        await self.db.refresh(task)
        return task

    async def bulk_update_status(
        self,
        task_ids: List[UUID],
        status: TaskStatus,
        updated_by_id: UUID
    ) -> int:
        """Bulk update status for multiple tasks"""
        now = datetime.now(timezone.utc)
        
        result = await self.db.execute(
            select(Task).where(
                Task.id.in_(task_ids),
                Task.deleted_at.is_(None)
            )
        )
        tasks = result.scalars().all()

        for task in tasks:
            task.status = status
            task.status_changed_at = now
            task.updated_by_id = updated_by_id

        await self.db.commit()
        return len(tasks)