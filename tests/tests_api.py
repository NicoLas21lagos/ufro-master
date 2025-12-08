import pytest
from fastapi.testclient import TestClient
from api.app import app

client = TestClient(app)

def test_health_check():
    response = client.get("/healthz")
    assert response.status_code == 200
    assert "status" in response.json()

def test_identify_without_auth():
    response = client.post("/identify-and-answer")
    assert response.status_code == 401

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from orchestrator.fuse import fuse_results

def test_fuse_identified():
    results = [
        {"success": True, "name": "Ana", "score": 0.9, "is_me": True},
        {"success": True, "name": "Luis", "score": 0.4, "is_me": True}
    ]
    
    result = fuse_results(results, threshold=0.75, margin=0.15)
    assert result["decision"] == "identified"
    assert result["identity"]["name"] == "Ana"

def test_fuse_ambiguous():
    results = [
        {"success": True, "name": "Ana", "score": 0.8, "is_me": True},
        {"success": True, "name": "Luis", "score": 0.75, "is_me": True}
    ]
    
    result = fuse_results(results, threshold=0.75, margin=0.15)
    assert result["decision"] == "ambiguous"

def test_fuse_unknown():
    results = [
        {"success": True, "name": "Ana", "score": 0.5, "is_me": True},
        {"success": True, "name": "Luis", "score": 0.4, "is_me": True}
    ]
    
    result = fuse_results(results, threshold=0.75, margin=0.15)
    assert result["decision"] == "unknown"