# orchestrator/pp1_client.py
import httpx
from datetime import datetime
from db.mongo import get_db

async def ask_rag(question, pp1_url, request_id, timeout_s=10.0):
    async with httpx.AsyncClient(timeout=timeout_s) as client:
        resp = await client.post(pp1_url, json={"question": question})
    db = await get_db()
    doc = {
        "request_id": request_id,
        "ts": datetime.utcnow(),
        "service_type": "pp1",
        "service_name": "UFRO-RAG",
        "endpoint": pp1_url,
        "latency_ms": resp.elapsed.total_seconds()*1000 if hasattr(resp, "elapsed") else None,
        "status_code": resp.status_code,
        "payload_size_bytes": len(resp.content),
        "result": resp.json() if "application/json" in resp.headers.get("content-type","") else None,
        "timeout": False,
        "error": None
    }
    await db.service_logs.insert_one(doc)
    return resp.json()
