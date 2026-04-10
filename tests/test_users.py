import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio #Este decorador le dice a pytest que esta función es asíncrona
async def test_register_user():
    """
    Prueba que un usuario puede registrarse correctamente y que
    la API no devuelve las contraseña en la respuesta.
    """
    
    # 1. Preparamos los datos que enviará el frontend
    user_data = {
        "email" : "test_automatizado@correo.com",
        "full_name" : "Usuario de Prueba",
        "password" : "superpassword123"
    }
    
    # 2. Ejecutamos la petición post
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/v1/users/", json=user_data)
        
    # 3. Verificaciones (Asserts)
    # Comprobamos que el código HTTP es 201 (Recurso creado)
    assert response.status_code == 201
    
    # Extraemos el json de la respuesta
    data = response.json()
    
    # Comprobamos que los datos devueltos coinciden con los enviados
    assert data["email"] == user_data["email"]
    assert data["full_name"] == user_data["full_name"]
    
    # Verificamos que la base de datos le asignó un id
    assert "id" in data
    
    # Verificación de seguridad: La contraseña nunca debe ser devuelta
    assert "password" not in data
    assert "hashed_password" not in data
