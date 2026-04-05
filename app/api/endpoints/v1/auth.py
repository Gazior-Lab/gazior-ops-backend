from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import auth as auth_schemas
from app.api import dependencies
from app.services.auth_service import AuthService


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

@router.get("/me", response_model=auth_schemas.UserResponse)
async def read_users_me(current_user: auth_schemas.UserResponse = Depends(dependencies.get_current_user)):
    return current_user


@router.post("/register", response_model=auth_schemas.UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    payload: auth_schemas.RegisterRequest,
    db: AsyncSession = Depends(dependencies.get_db),
):
    auth_service = AuthService(db)
    user = await auth_service.register_user(payload)
    return user


@router.post("/login", response_model=auth_schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(dependencies.get_db),
):
    auth_service = AuthService(db)
    user = await auth_service.authenticate_user(email=form_data.username, password=form_data.password)
    
    access_token = AuthService.create_access_token(data={"sub": str(user.email)})

    return auth_schemas.Token(
        access_token=access_token,
        token_type="bearer"
    )
