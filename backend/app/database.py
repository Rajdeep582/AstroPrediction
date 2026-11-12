import asyncio
import time

import certifi
from pymongo import ASCENDING, DESCENDING, AsyncMongoClient

from .config import MONGODB_DB_NAME, MONGODB_URI

client: AsyncMongoClient | None = None
db = None
last_error: str | None = None
connecting = False
_last_attempt = 0.0
_lock = asyncio.Lock()


async def connect_database():
    global client, db, last_error, _last_attempt
    if not MONGODB_URI:
        last_error = "MONGODB_URI is not set."
        return False
    _last_attempt = time.monotonic()
    new_client = AsyncMongoClient(
        MONGODB_URI,
        serverSelectionTimeoutMS=8000,
        connectTimeoutMS=8000,
        socketTimeoutMS=20000,
        maxPoolSize=50,
        minPoolSize=2,          # keep warm connections so first requests are fast
        maxIdleTimeMS=300000,
        retryWrites=True,
        retryReads=True,
        compressors="zlib",
        tlsCAFile=certifi.where(),
        appname="jyotish-studio",
    )
    try:
        await new_client.admin.command("ping")
        database = new_client[MONGODB_DB_NAME]
        await create_indexes(database)
    except Exception as exc:
        await new_client.close()
        last_error = str(exc).split(", Timeout")[0][:300]
        raise
    client, db, last_error = new_client, database, None
    return True


async def ensure_connected(min_interval: float = 15.0) -> bool:
    """Lazily (re)connect; throttled so a down cluster doesn't stall every request."""
    if db is not None:
        return True
    if time.monotonic() - _last_attempt < min_interval:
        return False
    global connecting
    async with _lock:
        if db is not None:
            return True
        connecting = True
        try:
            return await connect_database()
        except Exception:
            return False
        finally:
            connecting = False


async def close_database():
    global client, db
    if client:
        await client.close()
    client, db = None, None


async def create_indexes(database):
    await database.users.create_index([("id", ASCENDING)], unique=True)
    await database.users.create_index([("username_normalized", ASCENDING)], unique=True)
    await database.sessions.create_index([("token_hash", ASCENDING)], unique=True)
    await database.sessions.create_index([("expires_at", ASCENDING)], expireAfterSeconds=0)
    await database.profiles.create_index([("owner_id", ASCENDING), ("id", ASCENDING)], unique=True)
    await database.profiles.create_index([("owner_id", ASCENDING), ("updated_at", DESCENDING)])
    for name in ("kundli_records", "planetary_calculations", "divisional_charts", "dasha_records", "palmistry_sessions", "palm_images", "palm_features", "palm_reports", "combined_reports", "conversations", "messages", "saved_reports"):
        await database[name].create_index([("owner_id", ASCENDING), ("profile_id", ASCENDING), ("created_at", DESCENDING)])
    await database.knowledge_sources.create_index([("source_id", ASCENDING)], unique=True, sparse=True)
    await database.knowledge_chunks.create_index([("source_id", ASCENDING), ("chapter", ASCENDING)])
    await database.user_preferences.create_index([("owner_id", ASCENDING)], unique=True)
