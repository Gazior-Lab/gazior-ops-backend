from datetime import timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from app.core import security
from app.repositories.user import UserRepository
from app.utils.password import Hash
from app.schemas.auth import RegisterRequest
from app.core.exceptions import DuplicateError, CredentialsError
from app.models.user import User


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)

    async def authenticate_user(self, email: str, password: str) -> User:
        user = await self.user_repo.get_by_email(email=email)
        if not user:
            raise CredentialsError("Invalid email or password")
            
        if not Hash.verify_password(password, user.hashed_password):
            raise CredentialsError("Invalid email or password")
            
        if not user.is_active:
            raise CredentialsError("User account is disabled")

        # Update last login timestamp
        await self.user_repo.update_last_login(user)

        return user

    async def get_user_by_email(self, email: str) -> User | None:
        return await self.user_repo.get_by_email(email=email)

    async def register_user(self, payload: RegisterRequest) -> User:
        existing_user = await self.user_repo.get_by_email(email=payload.email)
        if existing_user:
            raise DuplicateError(f"User with email {payload.email} already exists")

        hashed_password = Hash.hash_password(payload.password)

        user = await self.user_repo.create(
            email=payload.email,
            full_name=payload.full_name,
            hashed_password=hashed_password
        )

        # Don't commit here - get_db dependency will commit automatically
        # Committing here causes double-commit issues
        return user

    @staticmethod
    def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
        return security.create_access_token(data=data, expires_delta=expires_delta)