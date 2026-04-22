# app/repositories/attachment.py
from datetime import datetime, timezone
from typing import Optional, List, Tuple

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.attachment import Attachment


class AttachmentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, attachment_id: int) -> Optional[Attachment]:
        """Get attachment by ID (excludes soft-deleted)."""
        result = await self.db.execute(
            select(Attachment).where(
                Attachment.id == attachment_id,
                Attachment.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def get_all_by_task(
        self,
        task_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> Tuple[List[Attachment], int]:
        """Get attachments for a task. Returns (attachments, total_count)."""
        query = select(Attachment).where(
            Attachment.task_id == task_id,
            Attachment.deleted_at.is_(None),
        )

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        query = query.order_by(Attachment.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        attachments = result.scalars().all()

        return attachments, total

    async def create(self, attachment: Attachment) -> Attachment:
        """Persist a new Attachment instance."""
        self.db.add(attachment)
        await self.db.commit()
        await self.db.refresh(attachment)
        return attachment

    async def update(self, attachment_id: int, **kwargs) -> Optional[Attachment]:
        """Update attachment fields."""
        attachment = await self.get_by_id(attachment_id)
        if not attachment:
            return None

        for key, value in kwargs.items():
            if hasattr(attachment, key):
                setattr(attachment, key, value)

        await self.db.commit()
        await self.db.refresh(attachment)
        return attachment

    async def soft_delete(self, attachment_id: int, deleted_by_id: int) -> bool:
        """Soft-delete an attachment."""
        attachment = await self.get_by_id(attachment_id)
        if not attachment:
            return False

        attachment.deleted_at = datetime.now(timezone.utc)
        attachment.updated_by_id = deleted_by_id
        await self.db.commit()
        return True
