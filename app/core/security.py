from passlib.context import CryptContext

# Configuracion del contexto de passlib para usar bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Este método verifica si una contraseña en texto plano coincide con un hash
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    # Este método genera el hash de una contraseña
    return pwd_context.hash(password)

