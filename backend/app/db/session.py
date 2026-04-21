from pymongo import MongoClient
from pymongo.database import Database

from app.core.config import settings

# Create MongoDB client
client: MongoClient = MongoClient(settings.mongodb_url)


def get_mongodb() -> Database:
    """Returns the MongoDB database instance."""
    return client[settings.mongodb_db_name]
