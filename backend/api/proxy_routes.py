import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi import APIRouter
from pydantic import BaseModel
from detection.engine import analyze
from storage.database import save_log, get_logs, get_stats

router = APIRouter()

class AnalyzeRequest(BaseModel):
    prompt: str
    use_semantic: bool = True

class AnalyzeResponse(BaseModel):
    decision: str
    final_score: int
    reasons: list[str]
    triggered_layers: list[str]
    layer_scores: dict
    log_id: int

@router.post("/analyze", response_model=AnalyzeResponse)
def analyze_prompt(request: AnalyzeRequest):
    result = analyze(request.prompt, use_semantic=request.use_semantic)
    log_id = save_log(request.prompt, result)
    result["log_id"] = log_id
    return result

@router.get("/logs")
def fetch_logs(limit: int = 50):
    return get_logs(limit=limit)

@router.get("/stats")
def fetch_stats():
    return get_stats()
