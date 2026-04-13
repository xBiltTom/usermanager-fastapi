from fastapi import HTTPException, status


class AppException(HTTPException):
    """
    Clase base para excepciones personalizadas de la aplicación.
    Proporciona estructura consistente con código de error y detalles opcionales.
    """

    def __init__(
        self,
        status_code: int,
        error_code: str,
        message: str,
        details: dict | None = None,
        headers: dict | None = None,
    ):
        self.error_code = error_code
        self.details = details or {}
        super().__init__(status_code=status_code, detail=message, headers=headers)


# ── Errores de usuario (4xx) ──────────────────────────────────────────────

class UserNotFoundError(AppException):
    """Se lanza cuando no se encuentra un usuario por ID o email."""

    def __init__(self, identifier: str | int | None = None):
        message = "Usuario no encontrado"
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="USER_NOT_FOUND",
            message=message,
            details={"identifier": str(identifier)} if identifier else None
        )


class DuplicateEmailError(AppException):
    """Se lanza cuando se intenta registrar un email ya existente."""

    def __init__(self, email: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            error_code="DUPLICATE_EMAIL",
            message="El correo electrónico ya está registrado en el sistema",
            details={"email": email}
        )


class InactiveUserError(AppException):
    """Se lanza cuando un usuario desactivado intenta autenticarse."""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="INACTIVE_USER",
            message="El usuario está desactivado"
        )


class InvalidCredentialsError(AppException):
    """Se lanza cuando las credenciales de login son incorrectas."""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="INVALID_CREDENTIALS",
            message="Correo electrónico o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"}
        )


class CannotDeleteOwnAccountError(AppException):
    """Se lanza cuando un usuario intenta eliminar su propia cuenta."""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="CANNOT_DELETE_OWN_ACCOUNT",
            message="No puedes eliminar tu propia cuenta"
        )


class InsufficientPermissionsError(AppException):
    """Se lanza cuando un usuario no tiene permisos suficientes."""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="INSUFFICIENT_PERMISSIONS",
            message="El usuario no tiene suficientes privilegios"
        )
