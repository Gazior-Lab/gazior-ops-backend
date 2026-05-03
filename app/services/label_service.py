from typing import Optional, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.label import LabelRepository
from app.repositories.project import ProjectRepository
from app.repositories.workspace_member import WorkspaceMemberRepository
from app.models.label import Label
from app.schemas.label import LabelCreate, LabelUpdate
from app.core.exceptions import (
    ObjectNotFoundError,
    ForbiddenError,
)


class LabelService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.label_repo = LabelRepository(db)
        self.project_repo = ProjectRepository(db)
        self.ws_member_repo = WorkspaceMemberRepository(db)

    async def _require_workspace_access(self, workspace_id: int, user_id: int) -> None:
        """Raise ForbiddenError if the user is not a member of the workspace."""
        ws_member = await self.ws_member_repo.get_by_user_and_workspace(
            user_id=user_id, workspace_id=workspace_id
        )
        if not ws_member:
            raise ForbiddenError(
                message="You don't have access to this workspace"
            )

    async def _require_project_admin(self, project_id: int, user_id: int) -> int:
        project = await self.project_repo.get_by_id(project_id)
        if not project:
            raise ObjectNotFoundError(
                message=f"Project {project_id} not found",
                details={"project_id": project_id},
            )
            
        ws_member = await self.ws_member_repo.get_by_user_and_workspace(
            user_id=user_id, workspace_id=project.workspace_id
        )
        
        from app.core.enums.common import WorkspaceMemberRole
        if not ws_member or ws_member.role not in [
            WorkspaceMemberRole.OWNER,
            WorkspaceMemberRole.ADMIN,
        ]:
            raise ForbiddenError(
                message="Only workspace owners and admins can manage labels"
            )
            
        return project.workspace_id

    async def _require_label_exists(self, label_id: int) -> Label:
        label = await self.label_repo.get_by_id(label_id)
        if not label:
            raise ObjectNotFoundError(
                message=f"Label {label_id} not found",
                details={"label_id": label_id},
            )
        return label

    async def get_label(self, label_id: int, current_user_id: int) -> Optional[Label]:
        label = await self._require_label_exists(label_id)
        project = await self.project_repo.get_by_id(label.project_id)
        if not project:
             raise ObjectNotFoundError(message="Project not found")
        await self._require_workspace_access(project.workspace_id, current_user_id)
        return label

    async def get_labels(
        self,
        project_id: int,
        current_user_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> Dict[str, Any]:
        project = await self.project_repo.get_by_id(project_id)
        if not project:
            raise ObjectNotFoundError(message="Project not found")
        await self._require_workspace_access(project.workspace_id, current_user_id)
        
        labels, total = await self.label_repo.get_all_by_project(
            project_id=project_id, skip=skip, limit=limit
        )
        return {"labels": labels, "total": total, "skip": skip, "limit": limit}

    async def create_label(
        self,
        label_data: LabelCreate,
        current_user_id: int,
    ) -> Label:
        await self._require_project_admin(label_data.project_id, current_user_id)

        label = Label(
            **label_data.model_dump(),
        )
        return await self.label_repo.create(label)

    async def update_label(
        self,
        label_id: int,
        label_data: LabelUpdate,
        current_user_id: int,
    ) -> Optional[Label]:
        label = await self._require_label_exists(label_id)
        await self._require_project_admin(label.project_id, current_user_id)

        update_data = label_data.model_dump(exclude_unset=True)
        if not update_data:
            return label

        return await self.label_repo.update(label_id, **update_data)

    async def delete_label(self, label_id: int, current_user_id: int) -> bool:
        label = await self._require_label_exists(label_id)
        await self._require_project_admin(label.project_id, current_user_id)
        return await self.label_repo.delete(label_id)
