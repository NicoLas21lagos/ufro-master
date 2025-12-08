# mcp_server/server.py
import asyncio
import json
from fastapi import FastAPI
from orchestrator.pp2_client import verify_all
from orchestrator.pp1_client import ask_rag
from orchestrator.fuse import fuse_verifications
from db.mongo import get_db
import yaml, os
from uuid import uuid4

app = FastAPI()
with open("conf/registry.yaml") as f:
    roster = yaml.safe_load(f).get("pp2_roster", [])

@app.post("/tool/identify_person")
async def identify_person(image_b64: str = None, image_url: str = None, timeout_s: float = 2.0):
    # Only allow one of image_b64/image_url - simplified for demo
    request_id = str(uuid4())
    # convert b64 to bytes if provided (omitted here for brevity) - expect clients to send image bytes in future
    # For demo: call roster with placeholder bytes
    img_bytes = b"\x00"  # placeholder - in practice decode b64 or fetch image_url
    results = await verify_all(img_bytes, roster, request_id, timeout_s=timeout_s)
    decision, identity, candidates = fuse_verifications(results, float(os.getenv("THRESHOLD",0.75)), float(os.getenv("MARGIN",0.08)))
    return {"request_id": request_id, "decision": decision, "identity": identity, "candidates": candidates}

@app.post("/tool/ask_normativa")
async def ask_normativa(question: str):
    pp1_url = os.getenv("PP1_URL", "http://localhost:8001/ask")
    request_id = str(uuid4())
    res = await ask_rag(question, pp1_url, request_id)
    return res

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)
