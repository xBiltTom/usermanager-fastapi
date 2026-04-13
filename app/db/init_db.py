import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud import crud_user
from app.schemas.user import UserCreate
from app.core.config import settings

logger = logging.getLogger(__name__)

async def init_db(db: AsyncSession) -> None:
    """Crea el primer superusuario si no existe"""
    user = await crud_user.get_user_by_email(db, email=settings.FIRST_SUPERUSER_EMAIL)
    if not user:
        logger.info("Creando primer superusuario: %s", settings.FIRST_SUPERUSER_EMAIL)
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER_EMAIL,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            full_name="Administrador principal"
        )
        await crud_user.create_superuser(db, user_in=user_in)
        logger.info("Superusuario creado exitosamente")
    else:
        logger.info("Superusuario ya existe, se omite la creación.")
    