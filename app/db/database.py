from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from app.config import settings
import ssl
import os

# Initialize db as None
db = None

def initialize_database():
    global db
    try:
        # Get MongoDB URL from environment
        mongodb_url = os.getenv('MONGODB_URL', settings.MONGODB_URL)
        print(f"Attempting to connect to MongoDB...")
        
        # Try connection without explicit SSL parameters first
        client = MongoClient(
            mongodb_url,
            serverSelectionTimeoutMS=10000,
            connectTimeoutMS=10000,
            socketTimeoutMS=10000
        )
        
        # Test the connection
        client.admin.command('ping')
        db = client.jnani_tuition
        print("Connected to MongoDB successfully!")
        return db
        
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
        # Try alternative connection method
        try:
            # Remove SSL parameters from URL and add them explicitly
            base_url = mongodb_url.split('?')[0]
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
            return db
        except Exception as e2:
            print(f"SSL fallback also failed: {e2}")
            db = None
            return None

def get_database():
    global db
    if db is None:
        db = initialize_database()
    return db 