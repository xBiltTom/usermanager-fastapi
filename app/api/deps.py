import uuid
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db
from app.crud import crud_user
from app.models.user import User

from typing import Annotated

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

async def get_current_user(
    db: Annotated[AsyncSession, Depends(get_db)],
    token : Annotated[str, Depends(oauth2_scheme)]
) -> User :
    """Depedencia para extraer y validar el usuario del token JWT"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWWW-Authenticate" : "Bearer"}
    )
    
    try : # El primer paso es desencriptar el token
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id : str = payload.get("sub")
        if user_id is None :
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    try :
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise credentials_exception
    
    user = await crud_user.get_user(db, id=user_uuid)
    if user is None :
        raise credentials_exception
    
    if not user.is_active :
        raise HTTPException(status_code=400, detail="Usuario inactivo")
    
    return user

def get_current_active_superuser(
    current_user : Annotated[User, Depends(get_current_user)]
):
    """Dependencia para verificar si el usuario logueado es superusuario"""
    if not current_user.is_superuser :
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El usuario no tiene suficientes privilegios"
        )
        
    return current_user