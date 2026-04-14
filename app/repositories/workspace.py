from datetime import datetime, timezone
from typing import Optional, List, Tuple

from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.workspace import Workspace
from app.core.enums.common import WorkspaceMemberRole


class WorkspaceRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, workspace_id: int) -> Optional[Workspace]:
        """Get workspace by ID (excludes soft-deleted)"""
        result = await self.db.execute(
            select(Workspace).where(
                Workspace.id == workspace_id,
                Workspace.deleted_at.is_(None)
            )
        )
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Optional[Workspace]:
        """Get workspace by slug (excludes soft-deleted)"""
        result = await self.db.execute(
            select(Workspace).where(
                Workspace.slug == slug,
                Workspace.deleted_at.is_(None)
            )
        )
        return result.scalar_one_or_none()

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
    ) -> Tuple[List[Workspace], int]:
        """
        Get workspaces with filtering, sorting, and pagination.
        Returns (workspaces, total_count)
        """
        # Build base query
        query = select(Workspace).where(Workspace.deleted_at.is_(None))

        # Apply filters
        if search:
            query = query.where(
                or_(
                    Workspace.name.ilike(f"%{search}%"),
                    Workspace.slug.ilike(f"%{search}%"),
                    Workspace.description.ilike(f"%{search}%")
                )
            )

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        # Apply pagination and ordering
        query = query.order_by(Workspace.created_at.desc())
        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        workspaces = result.scalars().all()

        return workspaces, total

    async def get_by_user_id(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> Tuple[List[Workspace], int]:
        """Get all workspaces where user is a member"""
        from app.models.workspace_member import WorkspaceMember

        # Build base query with join
        query = (
            select(Workspace)
            .join(WorkspaceMember, Workspace.id == WorkspaceMember.workspace_id)
            .where(
                WorkspaceMember.user_id == user_id,
                Workspace.deleted_at.is_(None),
                WorkspaceMember.deleted_at.is_(None)
            )
        )

        # Get total count
        count_query = (
            select(func.count())
            .select_from(
                select(Workspace.id)
                .join(WorkspaceMember, Workspace.id == WorkspaceMember.workspace_id)
                .where(
                    WorkspaceMember.user_id == user_id,
                    Workspace.deleted_at.is_(None),
                    WorkspaceMember.deleted_at.is_(None)
                )
                .subquery()
            )
        )
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        # Apply pagination and ordering
        query = query.order_by(Workspace.created_at.desc())
        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        workspaces = result.scalars().all()

        return workspaces, total

    async def create(self, workspace: Workspace) -> Workspace:
        """Create a new workspace"""
        self.db.add(workspace)
        await self.db.commit()
        await self.db.refresh(workspace)
        return workspace

    async def update(self, workspace_id: int, **kwargs) -> Optional[Workspace]:
        """Update workspace fields"""
        workspace = await self.get_by_id(workspace_id)
        if not workspace:
            return None

        for key, value in kwargs.items():
            if hasattr(workspace, key):
                setattr(workspace, key, value)

        await self.db.commit()
        await self.db.refresh(workspace)
        return workspace

    async def soft_delete(self, workspace_id: int, deleted_by_id: int) -> bool:
        """Soft delete a workspace"""
        workspace = await self.get_by_id(workspace_id)
        if not workspace:
            return False

        workspace.deleted_at = datetime.now(timezone.utc)
        workspace.updated_by_id = deleted_by_id

        await self.db.commit()
        return True

    async def slug_exists(self, slug: str, exclude_id: Optional[int] = None) -> bool:
        """Check if slug already exists"""
        query = select(func.count(Workspace.id)).where(
            Workspace.slug == slug,
            Workspace.deleted_at.is_(None)
        )
        if exclude_id:
            query = query.where(Workspace.id != exclude_id)

        result = await self.db.execute(query)
        count = result.scalar()
        return count > 0
