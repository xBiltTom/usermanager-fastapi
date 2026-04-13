import asyncio 
import logging
from app.db.session import AsyncSessionLocal
from app.db.init_db import init_db
          
logger = logging.getLogger(__name__)          
            
async def main() -> None:
    logger.info("Iniciando script de datos iniciales ...")
    async with AsyncSessionLocal() as db:
        await init_db(db)
    logger.info("Ejecución finalizada.")
    
if __name__ == "__main__" :
    asyncio.run(main())            