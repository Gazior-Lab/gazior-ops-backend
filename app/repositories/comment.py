# app/repositories/comment.py
from datetime import datetime, timezone
from typing import Optional, List, Tuple

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.comment import Comment


class CommentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, comment_id: int) -> Optional[Comment]:
        """Get comment by ID (excludes soft-deleted)."""
        result = await self.db.execute(
            select(Comment).where(
                Comment.id == comment_id,
                Comment.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def get_all_by_task(
        self,
        task_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> Tuple[List[Comment], int]:
        """Get comments for a task. Returns (comments, total_count)."""
        query = select(Comment).where(
            Comment.task_id == task_id,
            Comment.deleted_at.is_(None),
        )

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        query = query.order_by(Comment.created_at.asc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        comments = result.scalars().all()

        return comments, total

    async def create(self, comment: Comment) -> Comment:
        """Persist a new Comment instance."""
        self.db.add(comment)
        await self.db.commit()
        await self.db.refresh(comment)
        return comment

    async def update(self, comment_id: int, **kwargs) -> Optional[Comment]:
        """Update comment fields."""
        comment = await self.get_by_id(comment_id)
        if not comment:
            return None

        for key, value in kwargs.items():
            if hasattr(comment, key):
                setattr(comment, key, value)

        await self.db.commit()
        await self.db.refresh(comment)
        return comment

    async def soft_delete(self, comment_id: int, deleted_by_id: int) -> bool:
        """Soft-delete a comment."""
        comment = await self.get_by_id(comment_id)
        if not comment:
            return False

        comment.deleted_at = datetime.now(timezone.utc)
        comment.updated_by_id = deleted_by_id
        await self.db.commit()
        return True
