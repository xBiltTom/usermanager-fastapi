from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

# Importamos nuestras dependencias, schemas y crud
from app.db.session import get_db
from app.schemas.user import UserCreate, UserUpdate,UserResponse
from app.crud import crud_user

from app.models.user import User
from app.api.deps import get_current_user, get_current_active_superuser

from typing import Annotated, List
import uuid

# Instanciamos el router
router = APIRouter()

# Creación de una dependencia global de sesión con la base de datos
DBSession = Annotated[AsyncSession, Depends(get_db)]

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_in : UserCreate,db : DBSession):
    """Endpoint para registrar un nuevo usuario"""
    # Primero verificamos si el usuario que se quiere crear ya existe
    user = await crud_user.get_user_by_email(db, email=user_in.email);
    if user :
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo electrónico ya está registrado en el sistema"
        )
    # De no existir, creamos el usuario
    new_user = await crud_user.create_user(db,user_in=user_in)
    return new_user

@router.get("/me", response_model=UserResponse)
async def read_user_me(current_user : Annotated[User,Depends(get_current_user)]):
    """
    Obtener los datos del usuario actualmente autenticado.
    Gracias a Depends, FastApi se encarga de validar todo antes de llegar aquí 
    """
    return current_user

@router.get("/", response_model= List[UserResponse])
async def read_users(
    db : DBSession,
    current_user : Annotated[User,Depends(get_current_active_superuser)],
    skip : int = 0,
    limit : int = 100
):
    """
    Obtener todos los usuarios.
    Solo accesible para administradores (superusuarios)
    """
    users = await crud_user.get_users(db, skip = skip, limit=limit)
    return users

@router.patch("/{user_id}",response_model=UserResponse)
async def update_user(
    user_id : uuid.UUID,
    user_in : UserUpdate,
    db : DBSession,
    current_user : Annotated[User,Depends(get_current_active_superuser)]
): 
    """
    Actualizar un usuario específico por ID.
    Solo accesible para administradores (superusuarios).
    """
    
    user = await crud_user.get_user(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    user = await crud_user.update_user(db, db_user=user, user_in=user_in)
    return user
    