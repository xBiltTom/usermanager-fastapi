from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.endpoints import users, auth

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION
)

# Configuración de CORS
# En desarrollo se permite todo ["*""]. En producción solo el dominio del front
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


app.include_router(
    users.router,
    prefix=f"{settings.API_V1_STR}/users",
    tags=["Users"]
)

app.include_router(
    auth.router,
    prefix=f"{settings.API_V1_STR}/auth",
    tags=["Authentication"]
)

@app.get("/")
def root():
    return {"message": "Bienvenido a la API de gestión de usuarios"}