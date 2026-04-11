from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash

import uuid

from typing import List

async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    """
    Busca un usuario por su correo electrónico.
    Retorna el usuario si existe, o None si no se encuentra.
    """
    # En SQLAlchemy 2.0+ con AsyncSession, usamos 'select' y 'execute'
    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)
    return result.scalars().first() # Extraemos el primer objeto User del resultado

async def create_user(db: AsyncSession, user_in: UserCreate) -> User:
    """
    Crea un nuevo usuario en la db encriptando su contraseña
    """
    hashed_password = get_password_hash(user_in.password)
    
    db_user = User (
        email=user_in.email,
        hashed_password=hashed_password,
        full_name=user_in.full_name,
        is_active=user_in.is_active,
        is_superuser=False #Por defecto, al inicio nadie es superusuario
    )
    
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    
    return db_user

async def get_user(db: AsyncSession, id: uuid.UUID) -> User | None :
    """Buscar un usuario por su ID"""
    stmt = select(User).where(User.id == id)
    result = await db.execute(stmt)
    return result.scalars().first()

async def get_users(db : AsyncSession, skip: int = 0, limit: int = 100) -> List[User]:
    """Obtiene una lista de usuarios con paginación"""
    stmt = select(User).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

async def update_user(db : AsyncSession, *,db_user:User, user_in: UserUpdate) -> User :
    update_data = user_in.model_dump(exclude_unset=True)
    
    if "password" in update_data:
        hashed_password = get_password_hash(update_data["password"])
        del update_data["password"]
        update_data["hashed_password"] = hashed_password
    
    for field, value in update_data.items() :
        setattr(db_user, field, value)
    
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def remove_user(db: AsyncSession, id : uuid.UUID) -> User | None :
    """Elimina un usuario de la base de datos físicamente"""
    stmt = select(User).where(User.id == id)
    result = await db.execute(stmt)
    user = result.scalars().first()
    
    if user :
        await db.delete(user)
        await db.commit()
    
    return user

async def create_superuser(db: AsyncSession, user_in: UserCreate) -> User:
    """
    Crea un usuario administrador (superusuario) en el sistema.
    A diferencia de create_user, este forzará is_superuser=True
    """
    
    hashed_password = get_password_hash(user_in.password)
    
    db_user = User(
        email = user_in.email,
        hashed_password = hashed_password,
        full_name = user_in.full_name,
        is_active=True,
        is_superuser=True # Para el superusuario es True
    )
    
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user
