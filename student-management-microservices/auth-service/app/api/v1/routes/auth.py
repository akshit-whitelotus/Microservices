from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import (get_current_user,get_token_payload,)
from app.db.database import get_db
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import (UserCreate,UserResponse,)
from app.schemas.token import Token, TokenPayload
from shared.auth.constants import ACCESS_TOKEN_TYPE
from app.services.auth_service import AuthService

router = APIRouter()

@router.post("/register",response_model=UserResponse,status_code=status.HTTP_201_CREATED,)
async def register( user: UserCreate,db: AsyncSession = Depends(get_db),):
    repo = UserRepository(db)
    service = AuthService(repo)
    return await service.register(user)
@router.post( "/login",response_model=Token,)
async def login(form_data: OAuth2PasswordRequestForm = Depends(),db: AsyncSession = Depends(get_db),):
    repo = UserRepository(db)
    service = AuthService(repo)
    token = await service.login(form_data.username,form_data.password,)
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    return {"access_token": token,"token_type": ACCESS_TOKEN_TYPE,}
@router.get("/me",response_model=UserResponse,)
async def get_me(current_user: User = Depends(get_current_user),):
    return current_user
@router.post("/verify",response_model=TokenPayload,)
async def verify_token(payload: TokenPayload = Depends(get_token_payload),):
    return payload