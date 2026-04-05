from fastapi import FastAPI
from app.core.config import settings
from app.api.v1.endpoints import users

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION
)

app.include_router(
    users.router,
    prefix=f"{settings.API_V1_STR}/users",
    tags=["Users"]
)

@app.get("/")
def root():
    return {"message": "Bienvenido a la API de gestión de usuarios"}