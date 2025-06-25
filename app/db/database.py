from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from app.config import settings

try:
    client = MongoClient(settings.MONGODB_URL)
    db = client.jnani_tuition
    print("Connected to MongoDB successfully!")
except ConnectionFailure:
    print("Failed to connect to MongoDB")
    db = None

def get_database():
    return db 