from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import get_password_hash

import uuid

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