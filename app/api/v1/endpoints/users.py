from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

# Importamos nuestras dependencias, schemas y crud
from app.db.session import get_db
from app.schemas.user import UserCreate, UserResponse
from app.crud import crud_user

from app.models.user import User
from app.api.deps import get_current_user

# Instanciamos el router
router = APIRouter()

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_in : UserCreate,db: AsyncSession = Depends(get_db)):
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
async def read_user_me(current_user : User = Depends(get_current_user)):
    """
    Obtener los datos del usuario actualmente autenticado.
    Gracias a Depends, FastApi se encarga de validar todo antes de llegar aquí 
    """
    return current_user
    