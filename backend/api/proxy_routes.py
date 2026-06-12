import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi import APIRouter
from pydantic import BaseModel
from detection.engine import analyze

router = APIRouter()

# This defines what the incoming request must look like
class AnalyzeRequest(BaseModel):
    prompt: str
    use_semantic: bool = True   # Client can disable Layer 2 if they want speed

# This defines what we send back
class AnalyzeResponse(BaseModel):
    decision: str           # "block", "flag", or "pass"
    final_score: int
    reasons: list[str]
    triggered_layers: list[str]
    layer_scores: dict

@router.post("/analyze", response_model=AnalyzeResponse)
def analyze_prompt(request: AnalyzeRequest):
    """
    Main endpoint. Receives a prompt, runs all 3 detection layers,
    returns the decision.
    """
    result = analyze(request.prompt, use_semantic=request.use_semantic)
    return result
