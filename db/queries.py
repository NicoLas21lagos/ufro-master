# db/queries.py
from datetime import datetime, timedelta
from db.mongo import get_db
from bson.son import SON

async def metrics_decisions(days=7):
    db = await get_db()
    since = datetime.utcnow() - timedelta(days=days)
    pipeline = [
        {"$match": {"ts": {"$gte": since}}},
        {"$group": {"_id": "$decision", "total": {"$sum":1}}}
    ]
    return list(await db.access_logs.aggregate(pipeline).to_list(length=None))
