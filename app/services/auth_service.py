from datetime import timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app import models
from app.core import security
from app.repositories.user import UserRepository
from app.utils.password import Hash


class AuthService:

    @staticmethod
    async def authenticate_user(db: AsyncSession, email: str, password: str):
        user_repo = UserRepository(db)
        user = await user_repo.get_by_email(email=email)
        if not user:
            return None
        if not Hash.verify_password(password, user.hashed_password):
            return None

        if not user.is_active:
            return None
        
        return user

    @staticmethod
    def create_access_token(data: dict, expires_delta: timedelta | None = None):
        return security.create_access_token(data=data, expires_delta=expires_delta)