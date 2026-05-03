from typing import Optional, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.update import UpdateRepository
from app.repositories.workspace_member import WorkspaceMemberRepository
from app.models.update import Update
from app.schemas.update import UpdateCreate, UpdateUpdate
from app.core.exceptions import (
    ObjectNotFoundError,
    ForbiddenError,
)


class UpdateService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.update_repo = UpdateRepository(db)
        self.ws_member_repo = WorkspaceMemberRepository(db)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    async def _require_workspace_access(self, workspace_id: int, user_id: int) -> None:
        """Ensure user is in the workspace."""
        ws_member = await self.ws_member_repo.get_by_user_and_workspace(
            user_id=user_id, workspace_id=workspace_id
        )
        if not ws_member:
            raise ForbiddenError(
                message="You don't have access to this workspace"
            )

    async def _require_update_exists(self, update_id: int) -> Update:
        """Return update or raise ObjectNotFoundError."""
        update_obj = await self.update_repo.get_by_id(update_id)
        if not update_obj:
            raise ObjectNotFoundError(
                message=f"Update {update_id} not found",
                details={"update_id": update_id},
            )
        return update_obj

    # ------------------------------------------------------------------
    # Update CRUD
    # ------------------------------------------------------------------

    async def get_update(self, update_id: int, current_user_id: int) -> Optional[Update]:
        update_obj = await self._require_update_exists(update_id)
        await self._require_workspace_access(update_obj.workspace_id, current_user_id)
        return update_obj

    async def get_updates(
        self,
        workspace_id: int,
        current_user_id: int,
        skip: int = 0,
        limit: int = 100,
        tag: Optional[str] = None,
        department: Optional[str] = None,
    ) -> Dict[str, Any]:
        await self._require_workspace_access(workspace_id, current_user_id)
        updates, total = await self.update_repo.get_all_by_workspace(
            workspace_id=workspace_id, skip=skip, limit=limit, tag=tag, department=department
        )
        return {"updates": updates, "total": total, "skip": skip, "limit": limit}

    async def create_update(
        self,
        update_data: UpdateCreate,
        current_user_id: int,
    ) -> Update:
        """Create a team update."""
        await self._require_workspace_access(update_data.workspace_id, current_user_id)

        update_obj = Update(
            **update_data.model_dump(),
            author_id=current_user_id,
        )
        return await self.update_repo.create(update_obj)

    async def update_update(
        self,
        update_id: int,
        update_data: UpdateUpdate,
        current_user_id: int,
    ) -> Optional[Update]:
        """Update an update. Only the author can modify their update."""
        update_obj = await self._require_update_exists(update_id)
        
        if update_obj.author_id != current_user_id:
            raise ForbiddenError(message="You can only edit your own updates")

        update_payload = update_data.model_dump(exclude_unset=True)
        if not update_payload:
            return update_obj
            
        return await self.update_repo.update(update_id, **update_payload)

    async def delete_update(self, update_id: int, current_user_id: int) -> bool:
        """Hard-delete an update. Author or workspace admin can delete."""
        update_obj = await self._require_update_exists(update_id)
        
        ws_member = await self.ws_member_repo.get_by_user_and_workspace(
            user_id=current_user_id, workspace_id=update_obj.workspace_id
        )
        
        from app.core.enums.common import WorkspaceMemberRole
        is_admin = ws_member and ws_member.role in [WorkspaceMemberRole.OWNER, WorkspaceMemberRole.ADMIN]
        
        if update_obj.author_id != current_user_id and not is_admin:
            raise ForbiddenError(message="You don't have permission to delete this update")

        return await self.update_repo.delete(update_id)
