from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./bustaTv.db"
    SECRET_API_KEY: str = "bustatv-dev-secret-key-changeme"
    BACKEND_URL: str = "http://localhost:8000"
    CORS_ORIGINS: str = (
        "http://localhost:5173,http://127.0.0.1:5173,"
        "http://localhost:5174,http://127.0.0.1:5174,"
        "http://localhost:5601,http://127.0.0.1:5601"
    )

    class Config:
        env_file = ".env"

settings = Settings()
