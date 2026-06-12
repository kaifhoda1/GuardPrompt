import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from rule_based import analyze as layer1_analyze
from semantic import analyze as layer2_analyze
from heuristic import analyze as layer3_analyze
from scorer import score as final_score


def analyze(text: str, use_semantic: bool = True) -> dict:
    """
    Master detection function.
    Runs all 3 layers and returns one final result.

    Args:
        text: the user prompt to analyze
        use_semantic: set False to skip Layer 2 (faster, no Ollama needed)

    Returns:
        Final combined result with decision, score, reasons
    """

    # Run Layer 1 - always runs, very fast
    l1 = layer1_analyze(text)

    # Early exit - if Layer 1 is very confident, skip the rest
    # Score 85 = high severity match, no need to ask Mistral
    if l1.get("highest_score", 0) >= 85:
        return {
            "decision": "block",
            "final_score": 85,
            "reasons": l1.get("reasons", []),
            "triggered_layers": ["rule_based"],
            "layer_scores": {
                "layer1_rule": 85,
                "layer2_semantic": 0,
                "layer3_heuristic": 0
            },
            "early_exit": True
        }

    # Run Layer 2 - semantic (Mistral), skip if disabled
    if use_semantic:
        l2 = layer2_analyze(text)
    else:
        l2 = {
            "triggered": False,
            "score": 0,
            "reason": "Semantic layer disabled",
            "threat_type": "none"
        }

    # Run Layer 3 - heuristic, always runs, very fast
    l3 = layer3_analyze(text)

    # Combine everything in the scorer
    result = final_score(l1, l2, l3)
    result["early_exit"] = False

    return result
