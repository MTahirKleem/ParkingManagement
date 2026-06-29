from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "ParkingManagement"
    ENVIRONMENT: str = "development"

    MONGO_URI: str = "mongodb://localhost:27017"
    MONGO_DB_NAME: str = "ParkingManagement"

    JWT_SECRET_KEY: str = "change-this-secret"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    BACKEND_CORS_ORIGINS: str = "http://localhost:3000"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()