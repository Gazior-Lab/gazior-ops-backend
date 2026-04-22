# app/services/initiative_service.py
from typing import Optional, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.initiative import InitiativeRepository
from app.repositories.workspace_member import WorkspaceMemberRepository
from app.models.initiative import Initiative
from app.schemas.initiative import InitiativeCreate, InitiativeUpdate
from app.core.enums.common import InitiativeHealthStatus, WorkspaceMemberRole
from app.core.exceptions import (
    DuplicateError,
    ObjectNotFoundError,
    ForbiddenError,
)


class InitiativeService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.initiative_repo = InitiativeRepository(db)
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
                message="Only workspace owners and admins can manage initiatives"
            )

    async def _require_initiative_exists(self, initiative_id: int) -> Initiative:
        """Return initiative or raise ObjectNotFoundError."""
        initiative = await self.initiative_repo.get_by_id(initiative_id)
        if not initiative:
            raise ObjectNotFoundError(
                message=f"Initiative {initiative_id} not found",
                details={"initiative_id": initiative_id},
            )
        return initiative

    # ------------------------------------------------------------------
    # Initiative CRUD
    # ------------------------------------------------------------------

    async def get_initiative(self, initiative_id: int) -> Optional[Initiative]:
        return await self.initiative_repo.get_by_id(initiative_id)

    async def get_initiatives(
        self,
        workspace_id: int,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        health_status: Optional[str] = None,
    ) -> Dict[str, Any]:
        initiatives, total = await self.initiative_repo.get_all_by_workspace(
            workspace_id=workspace_id,
            skip=skip,
            limit=limit,
            search=search,
            health_status=health_status,
        )
        return {"initiatives": initiatives, "total": total, "skip": skip, "limit": limit}

    async def create_initiative(
        self,
        initiative_data: InitiativeCreate,
        current_user_id: int,
    ) -> Initiative:
        """Create an initiative; caller must be workspace OWNER or ADMIN."""
        await self._require_workspace_admin(initiative_data.workspace_id, current_user_id)

        # Unique name check
        name_taken = await self.initiative_repo.name_exists_in_workspace(
            name=initiative_data.name,
            workspace_id=initiative_data.workspace_id,
        )
        if name_taken:
            raise DuplicateError(
                message=f"An initiative named '{initiative_data.name}' already exists in this workspace",
                details={"name": initiative_data.name, "workspace_id": initiative_data.workspace_id},
            )

        initiative = Initiative(
            **initiative_data.model_dump(),
            created_by_id=current_user_id,
            updated_by_id=current_user_id,
        )
        return await self.initiative_repo.create(initiative)

    async def update_initiative(
        self,
        initiative_id: int,
        initiative_data: InitiativeUpdate,
        current_user_id: int,
    ) -> Optional[Initiative]:
        """Update an initiative; caller must be workspace OWNER or ADMIN."""
        initiative = await self._require_initiative_exists(initiative_id)
        await self._require_workspace_admin(initiative.workspace_id, current_user_id)

        update_data = initiative_data.model_dump(exclude_unset=True)

        # Duplicate name check only when name is being changed
        if "name" in update_data and update_data["name"] != initiative.name:
            name_taken = await self.initiative_repo.name_exists_in_workspace(
                name=update_data["name"],
                workspace_id=initiative.workspace_id,
                exclude_id=initiative_id,
            )
            if name_taken:
                raise DuplicateError(
                    message=f"An initiative named '{update_data['name']}' already exists in this workspace",
                    details={"name": update_data["name"]},
                )

        if not update_data:
            return initiative

        update_data["updated_by_id"] = current_user_id
        return await self.initiative_repo.update(initiative_id, **update_data)

    async def delete_initiative(self, initiative_id: int, current_user_id: int) -> bool:
        """Soft-delete an initiative; caller must be workspace OWNER or ADMIN."""
        initiative = await self._require_initiative_exists(initiative_id)
        await self._require_workspace_admin(initiative.workspace_id, current_user_id)
        return await self.initiative_repo.soft_delete(initiative_id, current_user_id)
