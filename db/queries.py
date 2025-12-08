from datetime import datetime, timedelta
from db.mongo import get_db
from bson.son import SON

async def metrics_decisions(days=7, decision=None, user=None, ip=None):
    db = await get_db()
    since = datetime.utcnow() - timedelta(days=days)

    # Construimos el filtro dinámico
    match_filter = {"ts": {"$gte": since}}

    if decision:
        match_filter["decision"] = decision
    if user:
        match_filter["user"] = user
    if ip:
        match_filter["ip"] = ip

    pipeline = [
        {"$match": match_filter},
        {"$group": {"_id": "$decision", "total": {"$sum": 1}}},
        {"$sort": SON([("total", -1)])}
    ]

    return list(await db.access_logs.aggregate(pipeline).to_list(length=None))
