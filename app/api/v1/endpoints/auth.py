from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.security import verify_password, create_access_token
from app.crud import crud_user
from app.db.session import get_db

from typing import Annotated

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

@router.post("/login", response_model=dict)
@limiter.limit("5/minute")
async def login_access_token(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
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