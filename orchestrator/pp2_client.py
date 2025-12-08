# orchestrator/pp2_client.py
import httpx
import asyncio
from time import perf_counter
from datetime import datetime
from db.mongo import get_db

async def call_verifier(client, r, img_bytes, request_id, timeout_s=2.0):
    t0 = perf_counter()
    try:
        resp = await client.post(r["endpoint_verify"], files={"image": ("img.jpg", img_bytes, "image/jpeg")})
        latency_ms = (perf_counter()-t0)*1000
        return r["name"], resp, latency_ms, None
    except Exception as exc:
        latency_ms = (perf_counter()-t0)*1000
        return r["name"], None, latency_ms, str(exc)

async def verify_all(img_bytes, roster, request_id, timeout_s=2.0):
    async with httpx.AsyncClient(timeout=timeout_s) as client:
        tasks = [call_verifier(client, r, img_bytes, request_id, timeout_s) for r in roster if r.get("active", True)]
        results = await asyncio.gather(*tasks, return_exceptions=False)
    db = await get_db()
    for name, resp, latency_ms, err in results:
        doc = {
            "request_id": request_id,
            "ts": datetime.utcnow(),
            "service_type": "pp2",
            "service_name": name,
            "endpoint": next((r["endpoint_verify"] for r in roster if r["name"]==name), None),
            "latency_ms": latency_ms,
            "status_code": getattr(resp, "status_code", None),
            "payload_size_bytes": len(resp.content) if resp is not None else None,
            "result": resp.json() if resp is not None and "application/json" in resp.headers.get("content-type","") else None,
            "timeout": err is not None,
            "error": err
        }
        await db.service_logs.insert_one(doc)
    return results
