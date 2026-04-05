from datetime import datetime, timedelta
from typing import Any, Union
from jose import jwt
from app.core.config import settings

import bcrypt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Este método verifica si una contraseña en texto plano coincide con un hash
    return bcrypt.checkpw(plain_password.encode(),hashed_password.encode())

def get_password_hash(password: str) -> str:
    # Este método genera el hash de una contraseña
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def create_access_token(subject: Union[str,Any], expires_delta:timedelta = None) -> str :
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        
    to_encode = {"exp" : expire, "sub" : str(subject)}
    encoded_jwt = jwt.encode(to_encode,settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt
