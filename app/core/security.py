import bcrypt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Este método verifica si una contraseña en texto plano coincide con un hash
    return bcrypt.checkpw(plain_password.encode(),hashed_password.encode())

def get_password_hash(password: str) -> str:
    # Este método genera el hash de una contraseña
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

