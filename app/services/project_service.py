from datetime import datetime, timezone
from typing import Optional, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.project import ProjectRepository
from app.repositories.workspace_member import WorkspaceMemberRepository
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.core.enums.common import ProjectStatus, WorkspaceMemberRole
from app.core.exceptions import (
    DuplicateError,
    ObjectNotFoundError,
    ForbiddenError,
)


class ProjectService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.project_repo = ProjectRepository(db)
        self.ws_member_repo = WorkspaceMemberRepository(db)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    async def _require_workspace_admin(self, workspace_id: int, user_id: int) -> None:
        """Raise ForbiddenError if the user is not an OWNER or ADMIN of the workspace."""
        ws_member = await self.ws_member_repo.get_by_user_and_workspace(
            user_id=user_id, workspace_id=workspace_id
        )
        if not ws_member or ws_member.role not in [
            WorkspaceMemberRole.OWNER,
            WorkspaceMemberRole.ADMIN,
        ]:
            raise ForbiddenError(
                message="Only workspace owners and admins can manage projects"
            )

    async def _require_workspace_access(self, workspace_id: int, user_id: int) -> None:
        """Raise ForbiddenError if the user is not a member of the workspace."""
        ws_member = await self.ws_member_repo.get_by_user_and_workspace(
            user_id=user_id, workspace_id=workspace_id
        )
        if not ws_member:
            raise ForbiddenError(
                message="You don't have access to this workspace"
            )

    async def _require_project_exists(self, project_id: int) -> Project:
        """Return project or raise ObjectNotFoundError."""
        project = await self.project_repo.get_by_id(project_id)
        if not project:
            raise ObjectNotFoundError(
                message=f"Project {project_id} not found",
                details={"project_id": project_id},
            )
        return project

    # ------------------------------------------------------------------
    # Project CRUD
    # ------------------------------------------------------------------

    async def get_project(self, project_id: int, current_user_id: int) -> Optional[Project]:
        project = await self._require_project_exists(project_id)
        await self._require_workspace_access(project.workspace_id, current_user_id)
        return project

    async def get_projects(
        self,
        workspace_id: int,
        current_user_id: int,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        status: Optional[str] = None,
    ) -> Dict[str, Any]:
        await self._require_workspace_access(workspace_id, current_user_id)
        projects, total = await self.project_repo.get_all_by_workspace(
            workspace_id=workspace_id,
            skip=skip,
            limit=limit,
            search=search,
            status=status,
        )
        return {"projects": projects, "total": total, "skip": skip, "limit": limit}

    async def create_project(
        self,
        project_data: ProjectCreate,
        current_user_id: int,
    ) -> Project:
        """Create a project; caller must be workspace OWNER or ADMIN."""
        await self._require_workspace_admin(project_data.workspace_id, current_user_id)

        # Unique identifier check (composite: workspace_id + identifier)
        identifier_taken = await self.project_repo.identifier_exists_in_workspace(
            identifier=project_data.identifier,
            workspace_id=project_data.workspace_id,
        )
        if identifier_taken:
            raise DuplicateError(
                message=f"Identifier '{project_data.identifier}' is already used in this workspace",
                details={
                    "identifier": project_data.identifier,
                    "workspace_id": project_data.workspace_id,
                },
            )

        # Unique name check
        name_taken = await self.project_repo.name_exists_in_workspace(
            name=project_data.name,
            workspace_id=project_data.workspace_id,
        )
        if name_taken:
            raise DuplicateError(
                message=f"A project named '{project_data.name}' already exists in this workspace",
                details={"name": project_data.name, "workspace_id": project_data.workspace_id},
            )

        project = Project(
            **project_data.model_dump(),
            created_by_id=current_user_id,
            updated_by_id=current_user_id,
        )
        return await self.project_repo.create(project)

    async def update_project(
        self,
        project_id: int,
        project_data: ProjectUpdate,
        current_user_id: int,
    ) -> Optional[Project]:
        """Update a project; caller must be workspace OWNER or ADMIN."""
        project = await self._require_project_exists(project_id)
        await self._require_workspace_admin(project.workspace_id, current_user_id)

        update_data = project_data.model_dump(exclude_unset=True)

        # Duplicate name check only when name is being changed
        if "name" in update_data and update_data["name"] != project.name:
            name_taken = await self.project_repo.name_exists_in_workspace(
                name=update_data["name"],
                workspace_id=project.workspace_id,
                exclude_id=project_id,
            )
            if name_taken:
                raise DuplicateError(
                    message=f"A project named '{update_data['name']}' already exists in this workspace",
                    details={"name": update_data["name"]},
                )

        if not update_data:
            return project

        # Track status change timestamp
        if "status" in update_data and update_data["status"] != project.status:
            update_data["status_changed_at"] = datetime.now(timezone.utc)

        update_data["updated_by_id"] = current_user_id
        return await self.project_repo.update(project_id, **update_data)

    async def delete_project(self, project_id: int, current_user_id: int) -> bool:
        """Soft-delete a project; caller must be workspace OWNER or ADMIN."""
        project = await self._require_project_exists(project_id)
        await self._require_workspace_admin(project.workspace_id, current_user_id)
        return await self.project_repo.soft_delete(project_id, current_user_id)
