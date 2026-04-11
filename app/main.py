from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import HTTPException
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.core.config import settings
from app.api.v1.endpoints import users, auth

from app.db.session import AsyncSessionLocal
from sqlalchemy import text

from app.utils.errors import http_exception_handler, generic_exception_handler

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Configuración de CORS
# En desarrollo se permite todo ["*""]. En producción solo el dominio del front
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
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
@limiter.limit("30/minute")
def root(request: Request):
    return {"message": "Bienvenido a la API de gestión de usuarios"}


@app.get("/health", tags=["Health"])
async def health_check():
    try:
        async with AsyncSessionLocal() as db:
            await db.execute(text("SELECT 1"))
        return {"status" : "ok" , "database" : "connected"}
    except Exception:
        return {"status" : "error" , "database" : "disconnected"}