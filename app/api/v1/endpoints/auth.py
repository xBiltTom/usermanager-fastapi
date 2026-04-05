from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import verify_password, create_access_token
from app.crud import crud_user
from app.db.session import get_db

router = APIRouter()

@router.post("/login", response_model=dict)
async def login_access_token(
    db: AsyncSession = Depends(get_db), 
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any :
    user = await crud_user.get_user_by_email(db, email=form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Correo electrónico o contraseña incorrectos",
            headers={"WWW-Authenticate" : "Bearer"}
        )
    
    return {
        "access_token" : create_access_token(subject=user.id),
        "token_type" : "bearer"
    }