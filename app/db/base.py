from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    # Aquí se pueden agregar campos comunes a todas las tablas de la db
    # como id, created_at, updated_at, etc.
    pass