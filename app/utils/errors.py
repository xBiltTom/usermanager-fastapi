import logging
import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from starlette.middleware.base import BaseHTTPMiddleware

from app.utils.exceptions import AppException

logger = logging.getLogger(__name__)
MAX_REQUEST_ID_LENGTH = 100


def _normalize_request_id(raw_request_id: str | None) -> str:
    """Acepta IDs razonables del cliente o genera uno nuevo."""
    if not raw_request_id:
        return str(uuid.uuid4())

    request_id = raw_request_id.strip()
    if not request_id or len(request_id) > MAX_REQUEST_ID_LENGTH:
        return str(uuid.uuid4())

    allowed_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_.")
    if any(char not in allowed_chars for char in request_id):
        return str(uuid.uuid4())

    return request_id


def _sanitize_validation_errors(errors: list[dict]) -> list[dict]:
    """Elimina valores de entrada para no exponer datos sensibles en logs."""
    sanitized_errors = []
    for error in errors:
        sanitized_errors.append(
            {
                "field": ".".join(str(loc) for loc in error.get("loc", [])),
                "message": error.get("msg", "Validation error"),
                "type": error.get("type", "validation_error"),
            }
        )

    return sanitized_errors


def _extract_http_exception_message(detail: object) -> tuple[str, dict | None]:
    """Normaliza el detail de HTTPException a un mensaje seguro y consistente."""
    if isinstance(detail, str):
        return detail, None

    if detail is None:
        return "HTTP error", None

    return "HTTP error", {"detail": detail}

# ── Middleware de Request ID ───────────────────────────────────────────────

class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware que inyecta un X-Request-ID único en cada petición.
    Si el cliente envía un header X-Request-ID, se reutiliza para trazabilidad.
    """

    async def dispatch(self, request: Request, call_next):
        request_id = _normalize_request_id(request.headers.get("X-Request-ID"))
        request.state.request_id = request_id

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id

        return response


# ── Helpers ────────────────────────────────────────────────────────────────

def _build_error_response(
    status_code: int,
    error_code: str,
    message: str,
    request: Request,
    details: dict | None = None,
) -> dict:
    """Construye una respuesta de error consistente."""
    body: dict = {
        "error": {
            "status": status_code,
            "code": error_code,
            "message": message,
        }
    }

    if details:
        body["error"]["details"] = details

    body["error"]["path"] = request.url.path
    body["error"]["timestamp"] = datetime.now(timezone.utc).isoformat()
    body["error"]["request_id"] = getattr(request.state, "request_id", None)

    return body


# ── Handlers ───────────────────────────────────────────────────────────────

async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """
    Handler para excepciones personalizadas de la aplicación.
    Loggea según la severidad y devuelve respuesta estructurada.
    """
    # Loggear según tipo de error
    if exc.status_code >= 500:
        logger.error(
            "Error del servidor en %s %s: %s",
            request.method,
            request.url.path,
            exc.detail,
            exc_info=True,
            extra={"request_id": getattr(request.state, "request_id", None)},
        )
    elif exc.status_code >= 400:
        logger.warning(
            "Error del cliente en %s %s: %s [%s]",
            request.method,
            request.url.path,
            exc.detail,
            exc.error_code,
            extra={"request_id": getattr(request.state, "request_id", None)},
        )

    return JSONResponse(
        status_code=exc.status_code,
        content=_build_error_response(
            status_code=exc.status_code,
            error_code=exc.error_code,
            message=exc.detail,
            request=request,
            details=exc.details if exc.details else None,
        ),
        headers=exc.headers,
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Handler genérico para HTTPException de FastAPI.
    Loggea con nivel diferenciado según el código de estado.
    """
    # Logging diferenciado por severidad
    if exc.status_code >= 500:
        logger.error(
            "HTTP 5xx en %s %s: %s",
            request.method,
            request.url.path,
            exc.detail,
            extra={"request_id": getattr(request.state, "request_id", None)},
        )
    elif exc.status_code >= 400:
        logger.warning(
            "HTTP 4xx en %s %s: %s",
            request.method,
            request.url.path,
            exc.detail,
            extra={"request_id": getattr(request.state, "request_id", None)},
        )

    # Determinar código de error machine-readable
    error_code_map = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        405: "METHOD_NOT_ALLOWED",
        409: "CONFLICT",
        422: "VALIDATION_ERROR",
        429: "RATE_LIMIT_EXCEEDED",
    }
    error_code = error_code_map.get(exc.status_code, "HTTP_ERROR")
    message, details = _extract_http_exception_message(exc.detail)

    return JSONResponse(
        status_code=exc.status_code,
        content=_build_error_response(
            status_code=exc.status_code,
            error_code=error_code,
            message=message,
            request=request,
            details=details,
        ),
        headers=exc.headers,
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """
    Handler para errores de validación de Pydantic/FastAPI (422).
    Reformatea los errores para que sean más legibles y consistentes.
    """
    logger.warning(
        "Error de validación en %s %s",
        request.method,
        request.url.path,
        extra={
            "request_id": getattr(request.state, "request_id", None),
            "validation_errors": _sanitize_validation_errors(exc.errors()),
        },
    )

    # Reformatear errores de validación para que sean más claros
    formatted_errors = _sanitize_validation_errors(exc.errors())

    return JSONResponse(
        status_code=422,
        content=_build_error_response(
            status_code=422,
            error_code="VALIDATION_ERROR",
            message="Error de validación en los datos enviados",
            request=request,
            details={"fields": formatted_errors},
        ),
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handler de último recurso para excepciones no manejadas.
    Loggea el stack trace completo pero devuelve mensaje genérico al cliente.
    """
    logger.error(
        "Error inesperado en %s %s: %s",
        request.method,
        request.url.path,
        str(exc),
        exc_info=True,
        extra={"request_id": getattr(request.state, "request_id", None)},
    )

    return JSONResponse(
        status_code=500,
        content=_build_error_response(
            status_code=500,
            error_code="INTERNAL_SERVER_ERROR",
            message="Error interno del servidor",
            request=request,
        ),
    )


async def rate_limit_exception_handler(
    request: Request, exc: RateLimitExceeded
) -> JSONResponse:
    """Handler consistente para errores de rate limiting."""
    logger.warning(
        "Rate limit excedido en %s %s: %s",
        request.method,
        request.url.path,
        str(exc),
        extra={"request_id": getattr(request.state, "request_id", None)},
    )

    return JSONResponse(
        status_code=429,
        content=_build_error_response(
            status_code=429,
            error_code="RATE_LIMIT_EXCEEDED",
            message="Demasiadas solicitudes en poco tiempo",
            request=request,
            details={"detail": str(exc)},
        ),
    )
