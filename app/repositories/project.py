# app/repositories/project.py
from datetime import datetime, timezone
from typing import Optional, List, Tuple

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project


class ProjectRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, project_id: int) -> Optional[Project]:
        """Get project by ID (excludes soft-deleted)."""
        result = await self.db.execute(
            select(Project).where(
                Project.id == project_id,
                Project.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def get_all_by_workspace(
        self,
        workspace_id: int,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        status: Optional[str] = None,
    ) -> Tuple[List[Project], int]:
        """Get projects for a workspace with optional search/status filter.
        Returns (projects, total_count).
        """
        query = select(Project).where(
            Project.workspace_id == workspace_id,
            Project.deleted_at.is_(None),
        )

        if search:
            query = query.where(
                Project.name.ilike(f"%{search}%")
            )

        if status:
            query = query.where(Project.status == status)

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        query = query.order_by(Project.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        projects = result.scalars().all()

        return projects, total

    async def create(self, project: Project) -> Project:
        """Persist a new Project instance."""
        self.db.add(project)
        await self.db.commit()
        await self.db.refresh(project)
        return project

    async def update(self, project_id: int, **kwargs) -> Optional[Project]:
        """Update project fields."""
        project = await self.get_by_id(project_id)
        if not project:
            return None

        for key, value in kwargs.items():
            if hasattr(project, key):
                setattr(project, key, value)

        await self.db.commit()
        await self.db.refresh(project)
        return project

    async def soft_delete(self, project_id: int, deleted_by_id: int) -> bool:
        """Soft-delete a project."""
        project = await self.get_by_id(project_id)
        if not project:
            return False

        project.deleted_at = datetime.now(timezone.utc)
        project.updated_by_id = deleted_by_id
        await self.db.commit()
        return True

    async def identifier_exists_in_workspace(
        self,
        identifier: str,
        workspace_id: int,
        exclude_id: Optional[int] = None,
    ) -> bool:
        """Check whether a project with the same identifier already exists in the workspace."""
        query = select(func.count(Project.id)).where(
            Project.identifier == identifier,
            Project.workspace_id == workspace_id,
            Project.deleted_at.is_(None),
        )
        if exclude_id:
            query = query.where(Project.id != exclude_id)

        result = await self.db.execute(query)
        return (result.scalar() or 0) > 0

    async def name_exists_in_workspace(
        self,
        name: str,
        workspace_id: int,
        exclude_id: Optional[int] = None,
    ) -> bool:
        """Check whether a project with the same name already exists in the workspace."""
        query = select(func.count(Project.id)).where(
            Project.name == name,
            Project.workspace_id == workspace_id,
            Project.deleted_at.is_(None),
        )
        if exclude_id:
            query = query.where(Project.id != exclude_id)

        result = await self.db.execute(query)
        return (result.scalar() or 0) > 0
