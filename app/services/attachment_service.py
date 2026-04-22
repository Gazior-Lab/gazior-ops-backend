# app/services/attachment_service.py
from typing import Optional, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.attachment import AttachmentRepository
from app.repositories.task import TaskRepository
from app.repositories.workspace_member import WorkspaceMemberRepository
from app.models.attachment import Attachment
from app.schemas.attachment import AttachmentCreate, AttachmentUpdate
from app.core.exceptions import (
    ObjectNotFoundError,
    ForbiddenError,
)


class AttachmentService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.attachment_repo = AttachmentRepository(db)
        self.task_repo = TaskRepository(db)
        self.ws_member_repo = WorkspaceMemberRepository(db)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    async def _require_task_access(self, task_id: int, user_id: int) -> int:
        """Ensure task exists and user is in the task's workspace."""
        task = await self.task_repo.get_by_id(task_id)
        if not task:
            raise ObjectNotFoundError(
                message=f"Task {task_id} not found",
                details={"task_id": task_id},
            )
            
        ws_member = await self.ws_member_repo.get_by_user_and_workspace(
            user_id=user_id, workspace_id=task.workspace_id
        )
        if not ws_member:
            raise ForbiddenError(
                message="You don't have access to the workspace of this task"
            )
        
        return task.workspace_id

    async def _require_attachment_exists(self, attachment_id: int) -> Attachment:
        """Return attachment or raise ObjectNotFoundError."""
        attachment = await self.attachment_repo.get_by_id(attachment_id)
        if not attachment:
            raise ObjectNotFoundError(
                message=f"Attachment {attachment_id} not found",
                details={"attachment_id": attachment_id},
            )
        return attachment

    # ------------------------------------------------------------------
    # Attachment CRUD
    # ------------------------------------------------------------------

    async def get_attachment(self, attachment_id: int, current_user_id: int) -> Optional[Attachment]:
        attachment = await self._require_attachment_exists(attachment_id)
        await self._require_task_access(attachment.task_id, current_user_id)
        return attachment

    async def get_attachments(
        self,
        task_id: int,
        current_user_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> Dict[str, Any]:
        await self._require_task_access(task_id, current_user_id)
        attachments, total = await self.attachment_repo.get_all_by_task(
            task_id=task_id, skip=skip, limit=limit
        )
        return {"attachments": attachments, "total": total, "skip": skip, "limit": limit}

    async def create_attachment(
        self,
        attachment_data: AttachmentCreate,
        current_user_id: int,
    ) -> Attachment:
        """Create an attachment."""
        await self._require_task_access(attachment_data.task_id, current_user_id)

        attachment = Attachment(
            **attachment_data.model_dump(),
            uploader_id=current_user_id,
            created_by_id=current_user_id,
            updated_by_id=current_user_id,
        )
        return await self.attachment_repo.create(attachment)

    async def update_attachment(
        self,
        attachment_id: int,
        attachment_data: AttachmentUpdate,
        current_user_id: int,
    ) -> Optional[Attachment]:
        """Update an attachment. Only the uploader can update their attachment."""
        attachment = await self._require_attachment_exists(attachment_id)
        
        if attachment.uploader_id != current_user_id:
            raise ForbiddenError(message="You can only edit your own attachments")

        update_data = attachment_data.model_dump(exclude_unset=True)
        if not update_data:
            return attachment

        update_data["updated_by_id"] = current_user_id
        
        return await self.attachment_repo.update(attachment_id, **update_data)

    async def delete_attachment(self, attachment_id: int, current_user_id: int) -> bool:
        """Soft-delete an attachment. Uploader or workspace admin can delete."""
        attachment = await self._require_attachment_exists(attachment_id)
        workspace_id = await self._require_task_access(attachment.task_id, current_user_id)
        
        ws_member = await self.ws_member_repo.get_by_user_and_workspace(
            user_id=current_user_id, workspace_id=workspace_id
        )
        
        from app.core.enums.common import WorkspaceMemberRole
        is_admin = ws_member and ws_member.role in [WorkspaceMemberRole.OWNER, WorkspaceMemberRole.ADMIN]
        
        if attachment.uploader_id != current_user_id and not is_admin:
            raise ForbiddenError(message="You don't have permission to delete this attachment")

        return await self.attachment_repo.soft_delete(attachment_id, current_user_id)
