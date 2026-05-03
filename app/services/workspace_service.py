from typing import Optional, List, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.workspace import WorkspaceRepository
from app.repositories.workspace_member import WorkspaceMemberRepository
from app.repositories.project import ProjectRepository
from app.repositories.task import TaskRepository
from app.models.workspace import Workspace
from app.models.workspace_member import WorkspaceMember
from app.schemas.workspace import WorkspaceCreate, WorkspaceUpdate
from app.core.enums.common import WorkspaceMemberRole
from app.core.exceptions import DuplicateError, ObjectNotFoundError, ForbiddenError


class WorkspaceService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.workspace_repo = WorkspaceRepository(db)
        self.member_repo = WorkspaceMemberRepository(db)
        self.project_repo = ProjectRepository(db)
        self.task_repo = TaskRepository(db)

    async def get_workspace(self, workspace_id: int) -> Optional[Workspace]:
        """Get a single workspace by ID"""
        return await self.workspace_repo.get_by_id(workspace_id)

    async def get_workspace_by_slug(self, slug: str) -> Optional[Workspace]:
        """Get workspace by slug"""
        return await self.workspace_repo.get_by_slug(slug)

    async def get_workspaces(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
    ):
        """Get paginated workspaces with filters"""
        workspaces, total = await self.workspace_repo.get_all(
            skip=skip,
            limit=limit,
            search=search,
        )
        return {
            "workspaces": workspaces,
            "total": total,
            "skip": skip,
            "limit": limit,
        }

    async def get_user_workspaces(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
    ):
        """Get all workspaces where user is a member"""
        workspaces, total = await self.workspace_repo.get_by_user_id(
            user_id=user_id,
            skip=skip,
            limit=limit,
        )
        return {
            "workspaces": workspaces,
            "total": total,
            "skip": skip,
            "limit": limit,
        }

    async def create_workspace(
        self,
        workspace_data: WorkspaceCreate,
        current_user_id: int,
    ) -> Workspace:
        """Create a new workspace with the creator as OWNER"""
        # Check if slug already exists
        slug_exists = await self.workspace_repo.slug_exists(workspace_data.slug)
        if slug_exists:
            raise DuplicateError(
                message=f"Workspace with slug '{workspace_data.slug}' already exists",
                details={"slug": workspace_data.slug}
            )

        # Create workspace instance
        workspace = Workspace(
            **workspace_data.model_dump(),
            created_by_id=current_user_id,
            updated_by_id=current_user_id,
        )

        # Create workspace and add owner as member
        workspace = await self.workspace_repo.create(workspace)

        # Add creator as OWNER member
        owner_member = WorkspaceMember(
            workspace_id=workspace.id,
            user_id=current_user_id,
            role=WorkspaceMemberRole.OWNER,
        )
        await self.member_repo.create(owner_member)

        return workspace

    async def update_workspace(
        self,
        workspace_id: int,
        workspace_data: WorkspaceUpdate,
        current_user_id: int,
    ) -> Optional[Workspace]:
        """Update workspace with business logic"""
        # Check if workspace exists
        workspace = await self.workspace_repo.get_by_id(workspace_id)
        if not workspace:
            raise ObjectNotFoundError(
                message=f"Workspace {workspace_id} not found",
                details={"workspace_id": workspace_id}
            )

        # Check if user has permission (OWNER or ADMIN)
        member = await self.member_repo.get_by_user_and_workspace(
            user_id=current_user_id,
            workspace_id=workspace_id,
        )
        if not member or member.role not in [
            WorkspaceMemberRole.OWNER,
            WorkspaceMemberRole.ADMIN,
        ]:
            raise ForbiddenError(
                message="You don't have permission to update this workspace",
            )

        # Check slug uniqueness if being updated
        update_data = workspace_data.model_dump(exclude_unset=True)
        if "slug" in update_data and update_data["slug"] != workspace.slug:
            slug_exists = await self.workspace_repo.slug_exists(
                update_data["slug"],
                exclude_id=workspace_id,
            )
            if slug_exists:
                raise DuplicateError(
                    message=f"Workspace with slug '{update_data['slug']}' already exists",
                    details={"slug": update_data["slug"]}
                )

        if not update_data:
            return workspace

        # Add audit field
        update_data["updated_by_id"] = current_user_id

        return await self.workspace_repo.update(workspace_id, **update_data)

    async def delete_workspace(
        self,
        workspace_id: int,
        current_user_id: int,
    ) -> bool:
        """Soft delete a workspace (only OWNER can delete)"""
        # Check if user is OWNER
        member = await self.member_repo.get_by_user_and_workspace(
            user_id=current_user_id,
            workspace_id=workspace_id,
        )
        if not member or member.role != WorkspaceMemberRole.OWNER:
            raise ForbiddenError(
                message="Only workspace owner can delete",
            )

        return await self.workspace_repo.soft_delete(workspace_id, current_user_id)

    async def get_workspace_members(
        self,
        workspace_id: int,
        skip: int = 0,
        limit: int = 100,
    ):
        """Get all members of a workspace"""
        # Verify workspace exists
        workspace = await self.workspace_repo.get_by_id(workspace_id)
        if not workspace:
            raise ObjectNotFoundError(
                message=f"Workspace {workspace_id} not found",
                details={"workspace_id": workspace_id}
            )

        members, total = await self.member_repo.get_by_workspace(
            workspace_id=workspace_id,
            skip=skip,
            limit=limit,
        )
        return {
            "members": members,
            "total": total,
            "skip": skip,
            "limit": limit,
        }

    async def add_member(
        self,
        workspace_id: int,
        user_id: int,
        role: WorkspaceMemberRole,
        current_user_id: int,
    ) -> WorkspaceMember:
        """Add a member to workspace"""
        # Check if workspace exists
        workspace = await self.workspace_repo.get_by_id(workspace_id)
        if not workspace:
            raise ObjectNotFoundError(
                message=f"Workspace {workspace_id} not found",
                details={"workspace_id": workspace_id}
            )

        # Check if user has permission (OWNER or ADMIN)
        current_member = await self.member_repo.get_by_user_and_workspace(
            user_id=current_user_id,
            workspace_id=workspace_id,
        )
        if not current_member or current_member.role not in [
            WorkspaceMemberRole.OWNER,
            WorkspaceMemberRole.ADMIN,
        ]:
            raise ForbiddenError(
                message="You don't have permission to add members",
            )

        # Check if member already exists
        existing_member = await self.member_repo.get_by_user_and_workspace(
            user_id=user_id,
            workspace_id=workspace_id,
        )
        if existing_member:
            raise DuplicateError(
                message=f"User {user_id} is already a member of this workspace",
                details={"user_id": user_id, "workspace_id": workspace_id}
            )

        # Create new member
        new_member = WorkspaceMember(
            workspace_id=workspace_id,
            user_id=user_id,
            role=role,
        )
        return await self.member_repo.create(new_member)

    async def update_member_role(
        self,
        workspace_id: int,
        user_id: int,
        new_role: WorkspaceMemberRole,
        current_user_id: int,
    ) -> Optional[WorkspaceMember]:
        """Update a member's role"""
        # Only OWNER can update roles
        current_member = await self.member_repo.get_by_user_and_workspace(
            user_id=current_user_id,
            workspace_id=workspace_id,
        )
        if not current_member or current_member.role != WorkspaceMemberRole.OWNER:
            raise ForbiddenError(
                message="Only workspace owner can update member roles",
            )

        return await self.member_repo.update_member_role(
            workspace_id=workspace_id,
            user_id=user_id,
            role=new_role,
        )

    async def remove_member(
        self,
        workspace_id: int,
        user_id: int,
        current_user_id: int,
    ) -> bool:
        """Remove a member from workspace"""
        # Get the member to be removed
        member = await self.member_repo.get_by_user_and_workspace(
            user_id=user_id,
            workspace_id=workspace_id,
        )
        if not member:
            raise ObjectNotFoundError(
                message=f"User {user_id} is not a member of this workspace",
                details={"user_id": user_id, "workspace_id": workspace_id}
            )

        # Check permissions: user can remove themselves, or OWNER/ADMIN can remove others
        current_member = await self.member_repo.get_by_user_and_workspace(
            user_id=current_user_id,
            workspace_id=workspace_id,
        )

        # Can't remove the last OWNER
        if member.role == WorkspaceMemberRole.OWNER:
            owner_count = await self.member_repo.get_owner_count(workspace_id)
            if owner_count <= 1 and user_id != current_user_id:
                raise ForbiddenError(
                    message="Cannot remove the only owner from the workspace",
                )

        # Permission check
        is_self = user_id == current_user_id
        is_admin_or_owner = current_member and current_member.role in [
            WorkspaceMemberRole.OWNER,
            WorkspaceMemberRole.ADMIN,
        ]

        if not is_self and not is_admin_or_owner:
            raise ForbiddenError(
                message="You don't have permission to remove this member",
            )

        return await self.member_repo.soft_delete(member.id, current_user_id)

    async def get_workspace_stats(self, workspace_id: int) -> Dict[str, Any]:
        """Get workspace statistics (member count, projects, tasks, etc.)"""
        member_count = await self.member_repo.get_count_by_workspace(workspace_id)
        project_count = await self.project_repo.get_count_by_workspace(workspace_id)
        task_stats = await self.task_repo.get_stats_by_workspace(workspace_id)

        return {
            "total_members": member_count,
            "total_projects": project_count,
            "total_tasks": task_stats["total_tasks"],
            "total_active_tasks": task_stats["total_active_tasks"],
        }
