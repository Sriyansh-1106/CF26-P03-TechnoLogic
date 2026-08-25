import re
from typing import Dict, List, Any

AMBIGUOUS_PATTERNS = [
    (r"\b(quickly|asap|fast|immediately|urgent)\b", "Timeframe is vague. Please specify an exact SLA (e.g. 'within 24 hours')."),
    (r"\b(powerful|good|high-end|best)\b", "Quality descriptor is vague. Please specify hardware specs or exact budget cap (e.g. '< $3,000')."),
    (r"\b(cheap|standard|basic)\b", "Tier is unspecified. Please define an approved model catalog or cost limit."),
    (r"\b(reasonable|appropriate|sufficient)\b", "Subjective quantifier detected. Replace with a quantitative rule."),
]

def check_ambiguity(policy_text: str) -> Dict[str, Any]:
    """
    Scans natural language policy text for ambiguous or subjective terms.
    Returns:
        {
            'is_ambiguous': bool,
            'warnings': list[str],
            'suggestions': list[str]
        }
    """
    warnings = []
    suggestions = []

    for pattern, suggestion in AMBIGUOUS_PATTERNS:
        match = re.search(pattern, policy_text, re.IGNORECASE)
        if match:
            vague_word = match.group(0)
            warnings.append(f"Ambiguous term detected: '{vague_word}'")
            suggestions.append(suggestion)

    return {
        "is_ambiguous": len(warnings) > 0,
        "warnings": warnings,
        "suggestions": suggestions
    }
