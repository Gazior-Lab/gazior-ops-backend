from datetime import datetime, timezone
from typing import Optional, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.cycle import CycleRepository
from app.repositories.project import ProjectRepository
from app.repositories.workspace_member import WorkspaceMemberRepository
from app.models.cycle import Cycle
from app.schemas.cycle import CycleCreate, CycleUpdate
from app.core.exceptions import (
    ObjectNotFoundError,
    ForbiddenError,
)


class CycleService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.cycle_repo = CycleRepository(db)
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
                message="Only workspace owners and admins can manage cycles"
            )
            
        return project.workspace_id

    async def _require_cycle_exists(self, cycle_id: int) -> Cycle:
        cycle = await self.cycle_repo.get_by_id(cycle_id)
        if not cycle:
            raise ObjectNotFoundError(
                message=f"Cycle {cycle_id} not found",
                details={"cycle_id": cycle_id},
            )
        return cycle

    async def get_cycle(self, cycle_id: int, current_user_id: int) -> Optional[Cycle]:
        cycle = await self._require_cycle_exists(cycle_id)
        project = await self.project_repo.get_by_id(cycle.project_id)
        if not project:
            raise ObjectNotFoundError(message="Project not found")
        await self._require_workspace_access(project.workspace_id, current_user_id)
        return cycle

    async def get_cycles(
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
        
        cycles, total = await self.cycle_repo.get_all_by_project(
            project_id=project_id, skip=skip, limit=limit
        )
        return {"cycles": cycles, "total": total, "skip": skip, "limit": limit}

    async def create_cycle(
        self,
        cycle_data: CycleCreate,
        current_user_id: int,
    ) -> Cycle:
        await self._require_project_admin(cycle_data.project_id, current_user_id)

        cycle = Cycle(
            **cycle_data.model_dump(),
            created_by_id=current_user_id,
            updated_by_id=current_user_id,
        )
        return await self.cycle_repo.create(cycle)

    async def update_cycle(
        self,
        cycle_id: int,
        cycle_data: CycleUpdate,
        current_user_id: int,
    ) -> Optional[Cycle]:
        cycle = await self._require_cycle_exists(cycle_id)
        await self._require_project_admin(cycle.project_id, current_user_id)

        update_data = cycle_data.model_dump(exclude_unset=True)
        if not update_data:
            return cycle

        if "status" in update_data and update_data["status"] != cycle.status:
            update_data["status_changed_at"] = datetime.now(timezone.utc)

        update_data["updated_by_id"] = current_user_id
        return await self.cycle_repo.update(cycle_id, **update_data)

    async def delete_cycle(self, cycle_id: int, current_user_id: int) -> bool:
        cycle = await self._require_cycle_exists(cycle_id)
        await self._require_project_admin(cycle.project_id, current_user_id)
        return await self.cycle_repo.soft_delete(cycle_id, current_user_id)
