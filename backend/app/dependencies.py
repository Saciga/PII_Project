from typing import Generator
from pymongo.database import Database
from app.db.session import get_mongodb


def get_db() -> Generator[Database, None, None]:
    """Dependency to get a MongoDB database instance."""
    yield get_mongodb()
