# tests/mock_pp2.py
from fastapi import FastAPI, UploadFile, File
app = FastAPI()
@app.post("/verify")
async def verify(image: UploadFile = File(...)):
    # dummy: always return random-ish score
    import random
    return {"is_me": False, "score": round(random.uniform(0.0, 1.0), 2)}
