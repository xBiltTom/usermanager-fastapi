import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_login_user(client: AsyncClient):
    """
    Este test va a probar que un usario que ya existe puede iniciar sesión y obtener un JWT.
    """
    # 1. Preparamos y registramos el usuario de pruebas
    user_data = {
        "email" : "login_test@testemail.com",
        "full_name" : "Usuario para Login",
        "password" : "login_seguro_123"
    }
    
    # Luego, creamos el usuario
    await client.post("/api/v1/users/", json=user_data)
    
    # 2. Preparamos las credenciales para el login (Estándar OAuth2)
    # Importante recordar que OAuth2 exige que el campo para el correo se llame "username"
    login_data = {
        "username" : user_data["email"],
        "password" : user_data["password"]
    }
    
    # 3. Ejecutamos la petición post de Login
    # Importante: Usamos 'data=login_data'  en lugar de 'json=...' puesto que necesitamos simular un formulario
    response = await client.post("/api/v1/auth/login", data=login_data)
    
    # 4. Verificaciones
    assert response.status_code == 200
    
    tokens = response.json()
    assert  "access_token" in tokens
    assert tokens["token_type"] == "bearer"
    
    # Opcional: Se verifica que el token recibido sea un string razonablemente largo (JWT real)
    assert len(tokens["access_token"]) > 50
