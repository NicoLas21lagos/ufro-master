# api/app.py
import os, io, hashlib
from uuid import uuid4
from time import perf_counter
from datetime import datetime
from fastapi import FastAPI, File, Form, UploadFile, Header, HTTPException
import yaml
from orchestrator.pp2_client import verify_all
from orchestrator.pp1_client import ask_rag
from orchestrator.fuse import fuse_verifications
from db.mongo import get_db

app = FastAPI()
# Load roster
with open("conf/registry.yaml") as f:
    conf = yaml.safe_load(f)
ROSTER = conf.get("pp2_roster", [])
PP1_URL = os.getenv("PP1_URL", "http://localhost:8001/ask")
THRESHOLD = float(os.getenv("THRESHOLD", 0.75))
MARGIN = float(os.getenv("MARGIN", 0.08))
PP2_TIMEOUT_S = float(os.getenv("PP2_TIMEOUT_S", 2.0))

@app.post("/identify-and-answer")
async def identify_and_answer(
    image: UploadFile = File(...),
    question: str = Form(None),
    x_user_id: str = Header(None),
    x_user_type: str = Header("external"),
    authorization: str = Header(None)
):
    # basic auth
    if authorization != f"Bearer {os.getenv('SECRET_TOKEN','secret-token-123')}":
        raise HTTPException(status_code=401, detail="Unauthorized")
    request_id = str(uuid4())
    t0 = perf_counter()
    img_bytes = await image.read()
    # hash (don't store image)
    image_hash = hashlib.sha256(img_bytes).hexdigest()
    # call PP2s
    results = await verify_all(img_bytes, ROSTER, request_id, timeout_s=PP2_TIMEOUT_S)
    decision, identity, candidates = fuse_verifications(results, THRESHOLD, MARGIN)
    normativa_answer = None
    if question and decision == "identified":
        normativa_answer = await ask_rag(question, PP1_URL, request_id)
    timing_ms = round((perf_counter()-t0)*1000, 2)
    # insert access log
    db = await get_db()
    doc = {
      "request_id": request_id,
      "ts": datetime.utcnow(),
      "route": "/identify-and-answer",
      "user": {"id": x_user_id, "type": x_user_type, "role": "basic"},
      "input": {"has_image": True, "has_question": bool(question),
                "image_hash": image_hash, "size_bytes": len(img_bytes), "image_hash_ts": datetime.utcnow()},
      "decision": decision,
      "identity": identity,
      "timing_ms": timing_ms,
      "status_code": 200,
      "errors": None,
      "pp2_summary": {"queried": len(ROSTER)},
      "pp1_used": bool(question)
    }
    await db.access_logs.insert_one(doc)
    return {
        "decision": decision,
        "identity": identity,
        "candidates": candidates,
        "normativa_answer": normativa_answer,
        "timing_ms": timing_ms,
        "request_id": request_id
    }

@app.get("/healthz")
async def healthz():
    db = await get_db()
    try:
        await db.command("ping")
        return {"status":"ok","pp2_count": len(ROSTER)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
