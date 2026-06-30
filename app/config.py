from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb+srv://jnani-user:OhPQCKf15Q72ljwU@cluster0.imfj5bv.mongodb.net/jnani_tuition?retryWrites=true&w=majority&ssl=true&ssl_cert_reqs=CERT_NONE")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "jstsec2025jun")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    MEDIA_URL: str = os.getenv("MEDIA_URL", "http://localhost:8000")
    CLOUDINARY_URL: str = os.getenv("CLOUDINARY_URL", "")

    # Faculty remuneration. Pay is per class taught: a fixed rate for each
    # class of a fixed length. Time is recorded in minutes and the amount is
    # prorated by minutes taught (minutes / CLASS_MINUTES * RATE_PER_CLASS).
    RATE_PER_CLASS: float = float(os.getenv("RATE_PER_CLASS", "250"))
    CLASS_MINUTES: int = int(os.getenv("CLASS_MINUTES", "45"))

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings() 