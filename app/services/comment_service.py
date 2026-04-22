# app/services/comment_service.py
from datetime import datetime, timezone
from typing import Optional, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.comment import CommentRepository
from app.repositories.task import TaskRepository
from app.repositories.workspace_member import WorkspaceMemberRepository
from app.models.comment import Comment
from app.schemas.comment import CommentCreate, CommentUpdate
from app.core.exceptions import (
    ObjectNotFoundError,
    ForbiddenError,
)


class CommentService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.comment_repo = CommentRepository(db)
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

    async def _require_comment_exists(self, comment_id: int) -> Comment:
        """Return comment or raise ObjectNotFoundError."""
        comment = await self.comment_repo.get_by_id(comment_id)
        if not comment:
            raise ObjectNotFoundError(
                message=f"Comment {comment_id} not found",
                details={"comment_id": comment_id},
            )
        return comment

    # ------------------------------------------------------------------
    # Comment CRUD
    # ------------------------------------------------------------------

    async def get_comment(self, comment_id: int, current_user_id: int) -> Optional[Comment]:
        comment = await self._require_comment_exists(comment_id)
        await self._require_task_access(comment.task_id, current_user_id)
        return comment

    async def get_comments(
        self,
        task_id: int,
        current_user_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> Dict[str, Any]:
        await self._require_task_access(task_id, current_user_id)
        comments, total = await self.comment_repo.get_all_by_task(
            task_id=task_id, skip=skip, limit=limit
        )
        return {"comments": comments, "total": total, "skip": skip, "limit": limit}

    async def create_comment(
        self,
        comment_data: CommentCreate,
        current_user_id: int,
    ) -> Comment:
        """Create a comment."""
        await self._require_task_access(comment_data.task_id, current_user_id)

        comment = Comment(
            **comment_data.model_dump(),
            created_by_id=current_user_id,
            updated_by_id=current_user_id,
        )
        return await self.comment_repo.create(comment)

    async def update_comment(
        self,
        comment_id: int,
        comment_data: CommentUpdate,
        current_user_id: int,
    ) -> Optional[Comment]:
        """Update a comment. Only the author can update their comment."""
        comment = await self._require_comment_exists(comment_id)
        
        if comment.author_id != current_user_id:
            raise ForbiddenError(message="You can only edit your own comments")

        update_data = comment_data.model_dump(exclude_unset=True)
        if not update_data:
            return comment

        update_data["edited_at"] = datetime.now(timezone.utc)
        update_data["updated_by_id"] = current_user_id
        
        return await self.comment_repo.update(comment_id, **update_data)

    async def delete_comment(self, comment_id: int, current_user_id: int) -> bool:
        """Soft-delete a comment. Author or workspace admin can delete."""
        comment = await self._require_comment_exists(comment_id)
        workspace_id = await self._require_task_access(comment.task_id, current_user_id)
        
        ws_member = await self.ws_member_repo.get_by_user_and_workspace(
            user_id=current_user_id, workspace_id=workspace_id
        )
        
        from app.core.enums.common import WorkspaceMemberRole
        is_admin = ws_member and ws_member.role in [WorkspaceMemberRole.OWNER, WorkspaceMemberRole.ADMIN]
        
        if comment.author_id != current_user_id and not is_admin:
            raise ForbiddenError(message="You don't have permission to delete this comment")

        return await self.comment_repo.soft_delete(comment_id, current_user_id)
