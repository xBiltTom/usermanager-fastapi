import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_read_root():
    """
    Prueba que el endpoint raíz '/' devuelve status 200 y el mensaje de bienvenida.
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/")
        
    assert response.status_code == 200
    assert response.json() == {"message" : "Bienvenido a la API de gestión de usuarios"}
    
    
