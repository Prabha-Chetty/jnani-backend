from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from app.config import settings
import ssl

try:
    # Try connection without explicit SSL parameters first
    client = MongoClient(
        settings.MONGODB_URL,
        serverSelectionTimeoutMS=10000,
        connectTimeoutMS=10000,
        socketTimeoutMS=10000
    )
    
    # Test the connection
    client.admin.command('ping')
    db = client.jnani_tuition
    print("Connected to MongoDB successfully!")
    
except Exception as e:
    print(f"Failed to connect to MongoDB: {e}")
    # Try alternative connection method
    try:
        # Remove SSL parameters from URL and add them explicitly
        base_url = settings.MONGODB_URL.split('?')[0]
        client = MongoClient(
            base_url,
            ssl=True,
            ssl_cert_reqs=ssl.CERT_NONE,
            serverSelectionTimeoutMS=10000,
            connectTimeoutMS=10000,
            socketTimeoutMS=10000
        )
        client.admin.command('ping')
        db = client.jnani_tuition
        print("Connected to MongoDB with SSL fallback!")
    except Exception as e2:
        print(f"SSL fallback also failed: {e2}")
        db = None

def get_database():
    return db 