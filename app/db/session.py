#Este archivo se encargará de configurar la conexión a la base de datos y de proporcionar sesiones a cada uno de los endpoints
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.config import settings

# Creamos el motor asíncrono
# Echo sirve para ver las consultas SQL en la termminal, útil en desarrollo
engine = create_async_engine( #Engine es el objeto que maneja la conexión con la base de datos
    settings.DATABASE_URL,
    echo=True,
    future=True #Para usar la API moderna de SQLAlchemy
) #Este objeto es global, por lo tanto se crea una sola vez

# Creamos el generador de sesiones, no una sesión. Cada vez que se use, se obtiene una sesión.
AsyncSessionLocal = async_sessionmaker(
    bind=engine, # conecta las sesiones al engine
    class_=AsyncSession, # especifica que será de tipo async
    expire_on_commit=False
)

#Dependencia para inyectar la sesión en los endpoints de fastapi
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session