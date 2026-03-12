from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

_client: AsyncIOMotorClient | None = None


async def get_db():
    """Return the MongoDB database instance, creating the client on first call."""
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(settings.MONGODB_URI)
    return _client[settings.DB_NAME]


async def close_db():
    """Gracefully close the MongoDB connection."""
    global _client
    if _client is not None:
        _client.close()
        _client = None
