import logging
from fastapi import Request
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail" : exc.detail
        }
    )
    
async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error(
        "Error inesperado en %s %s: %s",
        request.method,
        request.url.path,
        str(exc),
        exc_info=True
    )
    
    return JSONResponse(
        status_code=500,
        content={"detail" : "Error interno del servidor"}
    )