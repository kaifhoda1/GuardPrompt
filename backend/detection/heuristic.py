import re
import math
from collections import Counter


def _token_count(text: str) -> int:
    """Rough token count — 1 token ≈ 4 characters."""
    return len(text) // 4


def _special_char_ratio(text: str) -> float:
    """What percentage of characters are special (not letters/numbers/spaces)."""
    if not text:
        return 0.0
    special = sum(1 for c in text if not c.isalnum() and c not in " \n\t.,!?'\"")
    return special / len(text)


def _repetition_score(text: str) -> float:
    """
    Detect repeated phrases using 2-word and 4-word chunks.
    High repetition = possible instruction override attempt.
    """
    words = text.lower().split()
    if len(words) < 4:
        return 0.0

    chunks2 = [" ".join(words[i:i+2]) for i in range(len(words) - 1)]
    counts2 = Counter(chunks2)
    repeated2 = sum(1 for c in counts2.values() if c > 1)
    score2 = repeated2 / len(chunks2) if chunks2 else 0.0

    if len(words) >= 8:
        chunks4 = [" ".join(words[i:i+4]) for i in range(len(words) - 3)]
        counts4 = Counter(chunks4)
        repeated4 = sum(1 for c in counts4.values() if c > 1)
        score4 = repeated4 / len(chunks4) if chunks4 else 0.0
    else:
        score4 = 0.0

    return max(score2, score4)


def _single_word_repetition(text: str) -> float:
    """
    Check if a single word dominates the prompt.
    If top word appears more than 30% of the time, that's suspicious.
    """
    words = text.lower().split()
    if len(words) < 6:
        return 0.0
    counts = Counter(words)
    top_count = counts.most_common(1)[0][1]
    return top_count / len(words)


def _has_base64_block(text: str) -> bool:
    """Check for long base64-looking strings (possible encoded attack)."""
    pattern = re.compile(r'[A-Za-z0-9+/]{40,}={0,2}')
    return bool(pattern.search(text))


def _has_hex_block(text: str) -> bool:
    """Check for long hex strings."""
    pattern = re.compile(r'([0-9a-fA-F]{2}\s?){20,}')
    return bool(pattern.search(text))


def _language_switch_detected(text: str) -> bool:
    """
    Detect if the prompt switches between scripts.
    e.g. English + Arabic or English + Chinese mid-sentence.
    """
    has_latin = bool(re.search(r'[a-zA-Z]{3,}', text))
    has_arabic = bool(re.search(r'[\u0600-\u06FF]', text))
    has_chinese = bool(re.search(r'[\u4e00-\u9fff]', text))
    has_cyrillic = bool(re.search(r'[\u0400-\u04FF]', text))

    foreign_scripts = sum([has_arabic, has_chinese, has_cyrillic])
    return has_latin and foreign_scripts >= 1


def _entropy(text: str) -> float:
    """
    Shannon entropy - measures randomness of characters.
    Normal text: 3.5-4.5
    Encoded/encrypted content: 5.5+
    """
    if not text:
        return 0.0
    counts = Counter(text)
    total = len(text)
    return -sum((c/total) * math.log2(c/total) for c in counts.values())


def analyze(text: str) -> dict:
    """
    Run Layer 3 heuristic checks on the input text.
    Returns a dict with score, triggered flag, and reasons.
    """
    score = 0
    reasons = []
    flags = {}

    # Check 1 - Prompt length
    token_count = _token_count(text)
    flags["token_count"] = token_count
    if token_count > 500:
        score += 50
        reasons.append(f"Unusually long prompt ({token_count} tokens)")
    elif token_count > 300:
        score += 40
        reasons.append(f"Long prompt ({token_count} tokens)")

    # Check 2 - Special character ratio
    sc_ratio = round(_special_char_ratio(text), 3)
    flags["special_char_ratio"] = sc_ratio
    if sc_ratio > 0.3:
        score += 35
        reasons.append(f"High special character ratio ({sc_ratio})")
    elif sc_ratio > 0.15:
        score += 15
        reasons.append(f"Elevated special character ratio ({sc_ratio})")

    # Check 3 - Repetition
    rep_score = round(_repetition_score(text), 3)
    flags["repetition_score"] = rep_score
    if rep_score > 0.4:
        score += 40
        reasons.append(f"High phrase repetition detected ({rep_score})")
    elif rep_score > 0.2:
        score += 20
        reasons.append(f"Moderate phrase repetition ({rep_score})")

    # Check 3b - Single word dominance
    word_dom = round(_single_word_repetition(text), 3)
    flags["word_dominance"] = word_dom
    if word_dom > 0.3:
        score += 40
        reasons.append(f"Single word dominates prompt ({word_dom} ratio) - possible repetition attack")

    # Check 4 - Base64
    has_b64 = _has_base64_block(text)
    flags["has_base64"] = has_b64
    if has_b64:
        score += 85
        reasons.append("Long base64-encoded block detected")

    # Check 5 - Hex encoding
    has_hex = _has_hex_block(text)
    flags["has_hex"] = has_hex
    if has_hex:
        score += 85
        reasons.append("Long hex-encoded block detected")

    # Check 6 - Language switching
    lang_switch = _language_switch_detected(text)
    flags["language_switch"] = lang_switch
    if lang_switch:
        score += 45
        reasons.append("Mixed language scripts detected (possible evasion)")

    # Check 7 - Entropy
    entropy_val = round(_entropy(text), 3)
    flags["entropy"] = entropy_val
    if entropy_val > 5.5:
        score += 30
        reasons.append(f"High entropy detected ({entropy_val}) - possible encoded content")

    # Cap score at 100
    score = min(score, 100)

    return {
        "triggered": score >= 40,
        "score": score,
        "reasons": reasons,
        "flags": flags
    }
