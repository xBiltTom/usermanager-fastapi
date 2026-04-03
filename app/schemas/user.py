import uuid
from pydantic import BaseModel, EmailStr, ConfigDict

# 1. Base: Propiedades que se comparten en todos los casos
class UserBase(BaseModel):
    email: EmailStr
    full_name: str | None = None
    is_active: bool = True

# 2. Create: Lo que exigimos cuando alguien se registra
class UserCreate(UserBase):
    password : str
    
    
# 3. Update: Lo que permitimos actualizar (todo es opcional)
class UserUpdate(BaseModel):
    email: EmailStr | None = None
    full_name : str | None = None
    password : str | None = None
    
# 4. Response: Lo que devolvemos al usuario 
class UserResponse(UserBase):
    id: uuid.UUID
    is_superuser: bool
    
    model_config = ConfigDict(from_attributes=True) # Sirve para sacar los datos del objeto ORM

