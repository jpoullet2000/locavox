from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Optional
from ..models.user import User, UserCreate, Token
from ..services import auth_service
from ..logger import setup_logger

# Set up logger for this module
logger = setup_logger(__name__)

router = APIRouter(
    tags=["auth"],
    responses={401: {"description": "Unauthorized"}},
)


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Get an access token using username and password"""
    user = await auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth_service.create_access_token(data={"sub": user.id})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", response_model=User)
async def register_user(user_data: UserCreate):
    """Register a new user"""
    try:
        user = await auth_service.register_user(user_data)
        return user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(auth_service.get_current_user)):
    """Get the current authenticated user"""
    return current_user
