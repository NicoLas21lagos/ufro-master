# db/mongo.py
import os
import motor.motor_asyncio

_client = None

def get_mongo_uri():
    return os.getenv("MONGO_URI", "mongodb://ufro:secret@localhost:27017")

async def get_db():
    global _client
    if _client is None:
        _client = motor.motor_asyncio.AsyncIOMotorClient(get_mongo_uri())
    return _client[os.getenv("DB_NAME", "ufro_master")]
