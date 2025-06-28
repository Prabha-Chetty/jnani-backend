from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    MONGODB_URL: str = os.getenv("DATABASE_URL", "mongodb+srv://jnani-user:OhPQCKf15Q72ljwU@cluster0.imfj5bv.mongodb.net/")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "jstsec2025jun")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"

settings = Settings() 