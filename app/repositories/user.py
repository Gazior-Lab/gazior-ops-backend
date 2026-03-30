
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User

class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: int) -> User | None:
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[User]:
        result = await self.db.execute(
            select(User).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def create(self, email: str, name: str, hashed_password: str) -> User:
        user = User(email=email, name=name, hashed_password=hashed_password)
        self.db.add(user)
        await self.db.flush()    # flush → get DB-generated id without full commit
        await self.db.refresh(user)  # refresh → load server_defaults (timestamps)
        return user

    async def delete(self, user: User) -> None:
        await self.db.delete(user)
        await self.db.flush()