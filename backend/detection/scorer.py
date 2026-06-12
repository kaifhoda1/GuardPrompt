def score(layer1: dict, layer2: dict, layer3: dict) -> dict:
    """
    Takes results from all 3 layers.
    Returns one final decision with combined score and reasons.
    """

    # Collect all scores
    l1_score = layer1.get("highest_score", 0)
    l2_score = layer2.get("score", 0)
    l3_score = layer3.get("score", 0)

    # Final score = highest score across all layers
    final_score = max(l1_score, l2_score, l3_score)

    # Collect all reasons from all layers
    all_reasons = []

    if layer1.get("reasons"):
        all_reasons.extend(layer1["reasons"])

    if layer2.get("triggered") and layer2.get("reason"):
        all_reasons.append(f"Semantic: {layer2['reason']}")

    if layer3.get("reasons"):
        all_reasons.extend(layer3["reasons"])

    # Remove duplicates while keeping order
    seen = set()
    unique_reasons = []
    for r in all_reasons:
        if r not in seen:
            seen.add(r)
            unique_reasons.append(r)

    # Make final decision
    if final_score >= 80:
        decision = "block"
    elif final_score >= 40:
        decision = "flag"
    else:
        decision = "pass"

    # Which layers triggered
    triggered_layers = []
    if layer1.get("triggered"):
        triggered_layers.append("rule_based")
    if layer2.get("triggered"):
        triggered_layers.append("semantic")
    if layer3.get("triggered"):
        triggered_layers.append("heuristic")

    return {
        "decision": decision,
        "final_score": final_score,
        "reasons": unique_reasons,
        "triggered_layers": triggered_layers,
        "layer_scores": {
            "layer1_rule": l1_score,
            "layer2_semantic": l2_score,
            "layer3_heuristic": l3_score
        }
    }
