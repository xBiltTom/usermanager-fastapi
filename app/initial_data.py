import asyncio 
from app.db.session import AsyncSessionLocal
from app.crud import crud_user
from app.schemas.user import UserCreate
from app.core.config import settings

async def init_db() -> None:
    """Función para inicializar los datos de la base de datos"""
    # Obtenemos una sesión de la db
    async with AsyncSessionLocal() as db:
        # Verificamos si el superusuario ya existe
        user = await crud_user.get_user_by_email(db, email=settings.FIRST_SUPERUSER_EMAIL)

        if not user:
            print(f"Creando primer superusuario con email: {settings.FIRST_SUPERUSER_EMAIL}")
            user_in = UserCreate(
                email=settings.FIRST_SUPERUSER_EMAIL,
                password=settings.FIRST_SUPERUSER_PASSWORD,
                full_name="Administrador Principal"
            )
            await crud_user.create_superuser(db,user_in=user_in)
            print("¡Superusuario creado exitosamente!")
        else:
            print("El superusuario ya existe en al base de datos. Saltando creación.")
            
async def main() -> None:
    print("Iniciando script de datos iniciales ...")
    await init_db()
    print("Ejecución finalizada.")
    
if __name__ == "__main__" :
    asyncio.run(main())            