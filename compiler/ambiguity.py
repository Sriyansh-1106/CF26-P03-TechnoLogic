"""
compiler/ambiguity.py
=====================
Semantic Ambiguity Firewall for the VeriFlow policy compiler.

Scans raw policy text for:
  • Unquantified vague terms  (e.g. "urgent", "large", "soon")
  • Missing numerical / currency thresholds
  • Over-broad role references (e.g. "senior staff")

Exported contract (used by teammates)
--------------------------------------
    check_ambiguity(policy_text: str) -> dict
"""

from __future__ import annotations

import re
from typing import Dict, List

# ---------------------------------------------------------------------------
# Vague-term catalogue
# ---------------------------------------------------------------------------

# Each entry: (pattern, human_label, suggested_fix)
_VAGUE_TERM_RULES: List[tuple[str, str, str]] = [
    # Time / urgency
    (r"\burgent(ly)?\b", "urgent", "specify a concrete SLA, e.g. 'within 4 business hours'"),
    (r"\bsoon\b", "soon", "replace with a concrete deadline, e.g. 'within 2 business days'"),
    (r"\bimmediately\b", "immediately", "specify 'within 1 hour' or an explicit deadline"),
    (r"\bquick(ly)?\b", "quick/quickly", "define maximum allowed processing time"),
    (r"\brapidly\b", "rapidly", "replace with a measurable SLA"),
    (r"\btimely\b", "timely", "define an explicit timeframe"),
    (r"\bpromptly\b", "promptly", "define an explicit timeframe"),
    # Size / quantity
    (r"\blarge\b", "large", "replace with a specific threshold, e.g. '> ₹1,00,000'"),
    (r"\bsmall\b", "small", "replace with a specific threshold, e.g. '< ₹10,000'"),
    (r"\bsignificant\b", "significant", "define a numeric threshold"),
    (r"\bsubstantial\b", "substantial", "define a numeric threshold"),
    (r"\bminor\b", "minor", "define a numeric threshold"),
    (r"\bmajor\b", "major", "define a numeric threshold"),
    # Cost / value
    (r"\bexpensive\b", "expensive", "specify a cost threshold, e.g. '> ₹50,000'"),
    (r"\bcheap\b", "cheap", "specify a cost threshold"),
    (r"\bhigh.?value\b", "high-value", "replace with an explicit monetary range"),
    (r"\blow.?value\b", "low-value", "replace with an explicit monetary range"),
    # Role seniority
    (r"\bsenior\b", "senior", "use an explicit role name, e.g. 'Finance_Director'"),
    (r"\bjunior\b", "junior", "use an explicit role name, e.g. 'Employee'"),
    (r"\bmanagement\b", "management", "use a specific role, e.g. 'Manager'"),
    (r"\bstaff\b", "staff", "use a specific role, e.g. 'Employee'"),
    # Process quality
    (r"\bappropriate(ly)?\b", "appropriate", "define the specific action or criteria required"),
    (r"\bsufficient\b", "sufficient", "define what 'sufficient' means quantitatively"),
    (r"\badequate\b", "adequate", "define measurable acceptance criteria"),
    (r"\breasonable\b", "reasonable", "replace with a concrete rule or threshold"),
    (r"\bnecessary\b", "necessary", "enumerate required conditions explicitly"),
]

# ---------------------------------------------------------------------------
# Currency / numeric-threshold detector
# ---------------------------------------------------------------------------

# Patterns that indicate a numeric threshold IS present — used to check that
# policies mentioning money/budgets actually include a hard number.
_CURRENCY_PATTERN = re.compile(
    r"""
    (                          # group: currency symbol or code
        ₹ | \$ | € | £ | ¥ |
        INR | USD | EUR | GBP
    )
    \s*                        # optional space
    [\d,]+                     # digits with optional thousands commas
    (\.\d+)?                   # optional decimal
    """,
    re.VERBOSE | re.IGNORECASE,
)

# Trigger words that SHOULD be accompanied by a currency/number
_THRESHOLD_TRIGGER = re.compile(
    r"\b(budget|amount|cost|price|value|spend|expenditure|limit|threshold|invoice|payment)\b",
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def check_ambiguity(policy_text: str) -> Dict:
    """Scan *policy_text* for semantic ambiguity.

    Parameters
    ----------
    policy_text:
        Raw natural-language policy string to analyse.

    Returns
    -------
    dict with keys:
        ``is_ambiguous``   – ``True`` if any issues were detected.
        ``detected_terms`` – List of ambiguous terms / issues found.
        ``warnings``       – Human-readable warning messages.
        ``suggested_fixes``– Actionable suggestion for each detected term.
    """
    text_lower = policy_text  # keep original case for display; regex uses IGNORECASE

    detected_terms: List[str] = []
    warnings: List[str] = []
    suggested_fixes: List[str] = []

    # 1. Vague-term scan ---------------------------------------------------
    for pattern, label, fix in _VAGUE_TERM_RULES:
        if re.search(pattern, text_lower, re.IGNORECASE):
            detected_terms.append(label)
            warnings.append(
                f"Ambiguous term detected: '{label}'. "
                f"Policies must use quantified, unambiguous language."
            )
            suggested_fixes.append(f"[{label}] → {fix}")

    # 2. Missing-currency-threshold scan ------------------------------------
    has_threshold_trigger = bool(_THRESHOLD_TRIGGER.search(policy_text))
    has_currency_value = bool(_CURRENCY_PATTERN.search(policy_text))

    if has_threshold_trigger and not has_currency_value:
        detected_terms.append("missing_currency_threshold")
        warnings.append(
            "Policy mentions a financial concept (budget/amount/cost/…) "
            "but contains no explicit currency threshold (e.g. ₹50,000 or $5,000). "
            "This will prevent the rule engine from evaluating approval limits."
        )
        suggested_fixes.append(
            "[missing_currency_threshold] → Add a concrete monetary threshold, "
            "e.g. 'purchases exceeding ₹50,000 require Finance_Director approval'."
        )

    return {
        "is_ambiguous": len(detected_terms) > 0,
        "detected_terms": detected_terms,
        "warnings": warnings,
        "suggested_fixes": suggested_fixes,
    }


# ---------------------------------------------------------------------------
# Convenience: batch check for a list of policies
# ---------------------------------------------------------------------------


def batch_check_ambiguity(policies: List[str]) -> List[Dict]:
    """Run :func:`check_ambiguity` on every string in *policies*.

    Returns a list of result dicts in the same order as *policies*.
    """
    return [check_ambiguity(p) for p in policies]
