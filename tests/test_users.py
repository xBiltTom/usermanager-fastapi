import pytest
from httpx import AsyncClient

@pytest.mark.asyncio #Este decorador le dice a pytest que esta función es asíncrona
async def test_register_user(client: AsyncClient):
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
    response = await client.post("/api/v1/users/", json=user_data)
        
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

@pytest.mark.asyncio
async def test_normal_user_cannot_read_all_users(client: AsyncClient):
    """
    Prueba que un usuario normal (no superusuario) recibe un error 403 Forbidden 
    al intentar acceder a una ruta exclusiva de administradores.
    """
    # 1. Registramos a un usuario normal
    user_data = {
        "email" : "cursioso@testmail.com",
        "full_name" : "Usuario Curioso",
        "password" : "password123"
    }
    
    await client.post("/api/v1/users/", json=user_data)
    
    # 2. Hacemos login para obtener su token
    login_data = {
        "username" : user_data["email"],
        "password" : user_data["password"]
    }
    
    login_response = await client.post("/api/v1/auth/login", data=login_data)
    token = login_response.json()["access_token"]
    
    # 3. Intentamos acceder a la lista de todos los usarios (ruta protegida)
    # Configuramos el header de autorización con el token bearer
    headers = {"Authorization" : f"Bearer {token}"}
    response = await client.get("/api/v1/users/", headers=headers)
    
    # 4. Verificaciones de seguridad
    # 403 es un error http de falta de permisos para acceder a la ruta
    assert response.status_code == 403
    assert response.json()["detail"] == "El usuario no tiene suficientes privilegios"
    
    