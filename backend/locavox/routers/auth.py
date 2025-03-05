from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from locavox.database import get_db_session
from locavox.models.sql.user import User as UserModel
from locavox.models.schemas.user import UserCreate, UserResponse, Token
from locavox.services import auth_service
from locavox.services.user_service import create_user, UserExistsError
from locavox.logger import setup_logger

# Set up logger for this module
logger = setup_logger(__name__)

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={401: {"description": "Unauthorized"}},
)


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db_session),
):
    """Get an access token using username and password"""
    user = await auth_service.authenticate_user(
        db, form_data.username, form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is disabled",
        )

    access_token = auth_service.create_access_token(data={"sub": user.id})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", response_model=UserResponse)
async def register_user(
    user_data: UserCreate, db: AsyncSession = Depends(get_db_session)
):
    """Register a new user"""
    try:
        user = await create_user(db, user_data)
        return user
    except UserExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )


@router.get("/me", response_model=UserResponse)
async def read_users_me(
    current_user: UserModel = Depends(auth_service.get_current_user),
):
    """Get the current authenticated user"""
    return current_user
