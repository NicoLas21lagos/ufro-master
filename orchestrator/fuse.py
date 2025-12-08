# orchestrator/fuse.py
from typing import List, Dict

def fuse_verifications(results: List[tuple], threshold: float, margin: float):
    """
    results: list of tuples (name, resp, latency, err)
    resp.json() expected: {"is_me": bool, "score": 0.88}
    """
    candidates = []
    for name, resp, latency, err in results:
        if resp is None:
            continue
        try:
            js = resp.json()
            score = float(js.get("score", 0.0))
        except Exception:
            score = 0.0
        candidates.append({"name": name, "score": score})
    candidates.sort(key=lambda x: x["score"], reverse=True)
    if not candidates:
        return "unknown", None, candidates
    top = candidates[0]
    if top["score"] >= threshold:
        second_score = candidates[1]["score"] if len(candidates) > 1 else 0.0
        if top["score"] - second_score >= margin:
            return "identified", top, candidates
        else:
            return "ambiguous", None, candidates
    else:
        return "unknown", None, candidates
