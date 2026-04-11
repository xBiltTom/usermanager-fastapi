from pydantic_settings import BaseSettings, SettingsConfigDict
#Base settings permite leer las variables de entorno, del sistema, etc.
#SettingsConfigDict provee la configuracion extra para decirle como cargar esas variables.

class Settings(BaseSettings): #Clase de configuración de la aplicación
    #Información básica de la API
    PROJECT_NAME: str = "User managment API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    #Base de datos
    DATABASE_URL: str
    #Seguridad (JWT)
    SECRET_KEY : str 
    ALGORITHM : str 
    ACCESS_TOKEN_EXPIRE_MINUTES : int
    
    #Base de datos para testing
    TEST_DATABASE_URL: str
    
    #Configuracion del primer superusuario
    FIRST_SUPERUSER_EMAIL: str
    FIRST_SUPERUSER_PASSWORD: str
    
    #Configuracion para que pydantic lea el archivo .env
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=True)
    
#Instanciamos la configuración para importarla en oiros archivos
settings = Settings()