import re
import json
import os
from typing import TypedDict

# ── Where the rules file lives ──────────────────────────────────────────────
RULES_PATH = os.path.join(
    os.path.dirname(__file__),   # backend/detection/
    "..", "..",                   # go up to project root
    "data", "rules", "injection_patterns.json"
)


class RuleMatch(TypedDict):
    category: str
    pattern: str
    severity: str
    score: int


class Layer1Result(TypedDict):
    triggered: bool
    matches: list[RuleMatch]
    highest_score: int
    decision: str        # "block" | "flag" | "pass"
    reasons: list[str]


def load_rules() -> dict:
    """Load the JSON ruleset from disk."""
    path = os.path.normpath(RULES_PATH)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _compile_patterns(rules: dict) -> list[tuple]:
    """
    Pre-compile all regex patterns.
    Returns list of (category, compiled_pattern, severity, score)
    """
    compiled = []
    severity_scores = rules["severity_scores"]
    categories = rules["categories"]

    for cat_name, cat_data in categories.items():
        severity = cat_data["severity"]
        score = severity_scores[severity]
        for raw_pattern in cat_data["patterns"]:
            try:
                compiled_re = re.compile(raw_pattern, re.IGNORECASE | re.DOTALL)
                compiled.append((cat_name, compiled_re, raw_pattern, severity, score))
            except re.error as e:
                # Bad pattern in JSON — log and skip, don't crash
                print(f"[WARN] Bad regex in category '{cat_name}': {raw_pattern} → {e}")

    return compiled


def analyze(text: str) -> Layer1Result:
    """
    Run Layer 1 rule-based detection on the input text.

    Args:
        text: The raw user prompt to analyze

    Returns:
        Layer1Result dict with decision, score, and matched rules
    """
    rules = load_rules()
    compiled_patterns = _compile_patterns(rules)
    thresholds = rules["thresholds"]

    matches: list[RuleMatch] = []
    highest_score = 0
    reasons: list[str] = []

    for (cat_name, compiled_re, raw_pattern, severity, score) in compiled_patterns:
        if compiled_re.search(text):
            matches.append({
                "category": cat_name,
                "pattern": raw_pattern,
                "severity": severity,
                "score": score
            })
            if score > highest_score:
                highest_score = score
            reason = f"{cat_name.replace('_', ' ').title()} detected ({severity} severity)"
            if reason not in reasons:
                reasons.append(reason)

    # Decide based on highest score across all matches
    if highest_score >= thresholds["block"]:
        decision = "block"
    elif highest_score >= thresholds["flag"]:
        decision = "flag"
    else:
        decision = "pass"

    return {
        "triggered": len(matches) > 0,
        "matches": matches,
        "highest_score": highest_score,
        "decision": decision,
        "reasons": reasons
    }