"""
compiler/parser.py
==================
LLM Few-Shot Policy Parser for the VeriFlow neurosymbolic safety compiler.

Primary path  : Google Gemini 1.5 Flash via ``google-generativeai``.
Fallback path : Loads matching mock JSON from the ``policies/`` directory
                (activated by env-var ``OFFLINE_MODE=True`` or any API error).

Exported contract (used by teammates)
--------------------------------------
    parse_policy(policy_text: str) -> WorkflowIR
"""

from __future__ import annotations

import json
import logging
import os
import re
import uuid
from pathlib import Path
from typing import Optional

from compiler.ir import StepNode, WorkflowIR

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

_POLICIES_DIR = Path(__file__).parent.parent / "policies"

# ---------------------------------------------------------------------------
# Few-shot examples embedded directly in the system prompt
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT = """
You are VeriFlow, a neurosymbolic safety compiler.
Your job is to convert a natural-language business policy into a structured
WorkflowIR JSON object.

## Output Schema (JSON only – no markdown fences, no extra text)
{
  "workflow_id": "<uuid-like string>",
  "title": "<concise title>",
  "trigger": "<business event that starts this workflow>",
  "steps": [
    {
      "id": "step_1",
      "action": "<snake_case verb phrase>",
      "role": "<Employee|Manager|Finance_Director|Admin>",
      "condition": "<Boolean guard or null>",
      "is_required": true,
      "dependencies": []
    }
    // … more steps
  ],
  "roles_allowed": ["Employee", "Manager", "Finance_Director", "Admin"]
}

## Rules
1. Use only roles: Employee, Manager, Finance_Director, Admin.
2. Every step must have a unique "id" starting from "step_1".
3. "condition" must be a valid Boolean expression or null.
4. Amount thresholds: Manager approves <= 20000; Finance_Director approves > 20000.
5. Output ONLY valid JSON. No explanation. No markdown.

## Few-Shot Examples

### Policy A
"When an employee needs to buy office supplies worth less than ₹5,000, the
manager must approve the purchase."

### Output A
{
  "workflow_id": "wf-example-001",
  "title": "Office Supplies Purchase Approval",
  "trigger": "Employee requests office supplies purchase",
  "steps": [
    {"id":"step_1","action":"submit_purchase_request","role":"Employee","condition":null,"is_required":true,"dependencies":[]},
    {"id":"step_2","action":"approve_budget","role":"Manager","condition":"amount < 5000","is_required":true,"dependencies":["step_1"]}
  ],
  "roles_allowed": ["Employee", "Manager"]
}

### Policy B
"Vendor invoices above ₹20,000 must be approved by the Finance Director after
the Manager reviews them. The Finance Director then releases the payment."

### Output B
{
  "workflow_id": "wf-example-002",
  "title": "High-Value Vendor Invoice Approval",
  "trigger": "Vendor invoice above ₹20,000 submitted",
  "steps": [
    {"id":"step_1","action":"submit_vendor_invoice","role":"Employee","condition":null,"is_required":true,"dependencies":[]},
    {"id":"step_2","action":"approve_budget","role":"Manager","condition":"amount > 20000","is_required":true,"dependencies":["step_1"]},
    {"id":"step_3","action":"finance_approval","role":"Finance_Director","condition":"amount > 20000","is_required":true,"dependencies":["step_2"]},
    {"id":"step_4","action":"release_payment","role":"Finance_Director","condition":null,"is_required":true,"dependencies":["step_3"]}
  ],
  "roles_allowed": ["Employee", "Manager", "Finance_Director"]
}
""".strip()


# ---------------------------------------------------------------------------
# Offline fallback helpers
# ---------------------------------------------------------------------------

def _keyword_to_fixture(policy_text: str) -> Optional[Path]:
    """Heuristically match *policy_text* to a fixture file in ``policies/``."""
    text_lower = policy_text.lower()
    candidates = {
        "vendor": _POLICIES_DIR / "vendor_payment.json",
        "invoice": _POLICIES_DIR / "vendor_payment.json",
        "payment": _POLICIES_DIR / "vendor_payment.json",
    }
    for keyword, path in candidates.items():
        if keyword in text_lower and path.exists():
            return path
    # Default generic fallback
    generic = _POLICIES_DIR / "generic_policy.json"
    return generic if generic.exists() else None


def _load_offline_fallback(policy_text: str) -> WorkflowIR:
    """Load the best-matching mock JSON and return a :class:`WorkflowIR`."""
    fixture_path = _keyword_to_fixture(policy_text)
    if fixture_path is None:
        logger.error("No offline fixture found. Returning minimal stub.")
        return WorkflowIR(
            workflow_id=f"wf-stub-{uuid.uuid4().hex[:8]}",
            title="Policy Stub (offline mode)",
            trigger="Unknown trigger",
            steps=[
                StepNode(id="step_1", action="manual_review", role="Admin")
            ],
            roles_allowed=["Admin"],
        )

    logger.info("Offline mode: loading fixture %s", fixture_path)
    data = json.loads(fixture_path.read_text(encoding="utf-8"))
    # Stamp a fresh ID so each call returns a distinct object
    data["workflow_id"] = f"{data['workflow_id']}-{uuid.uuid4().hex[:6]}"
    return WorkflowIR.from_dict(data)


# ---------------------------------------------------------------------------
# Gemini API call
# ---------------------------------------------------------------------------

def _call_gemini(policy_text: str) -> WorkflowIR:
    """Call Gemini 1.5 Flash and parse the JSON response into a WorkflowIR."""
    import google.generativeai as genai  # lazy import – not required offline

    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        raise EnvironmentError("GEMINI_API_KEY environment variable is not set.")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=_SYSTEM_PROMPT,
        generation_config=genai.GenerationConfig(
            response_mime_type="application/json",
            temperature=0.1,
            max_output_tokens=2048,
        ),
    )

    user_prompt = (
        f"Convert this business policy into WorkflowIR JSON:\n\n{policy_text}"
    )
    response = model.generate_content(user_prompt)
    raw_text = response.text.strip()

    # Strip accidental markdown fences if the model ignores the instruction
    if raw_text.startswith("```"):
        raw_text = re.sub(r"^```[a-z]*\n?", "", raw_text)
        raw_text = re.sub(r"\n?```$", "", raw_text)

    data = json.loads(raw_text)
    return WorkflowIR.from_dict(data)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def parse_policy(policy_text: str) -> WorkflowIR:
    """Convert a natural-language business policy string into a
    validated :class:`~compiler.ir.WorkflowIR` object.

    Execution order
    ---------------
    1. If ``OFFLINE_MODE=True`` env-var is set → load offline fixture.
    2. Otherwise attempt a live Gemini 1.5 Flash call.
    3. On **any** error (network, quota, parse) → fall back to offline fixture
       and emit a WARNING log.

    Parameters
    ----------
    policy_text:
        Raw natural-language policy string (any length).

    Returns
    -------
    WorkflowIR
        A validated Pydantic model ready for downstream stages.

    Raises
    ------
    This function **never raises** — it always returns a WorkflowIR (using the
    offline fixture when necessary).
    """
    offline_mode = os.environ.get("OFFLINE_MODE", "false").lower() in (
        "1", "true", "yes",
    )

    if offline_mode:
        logger.info("OFFLINE_MODE active — skipping Gemini API call.")
        return _load_offline_fallback(policy_text)

    try:
        return _call_gemini(policy_text)
    except Exception as exc:  # noqa: BLE001
        logger.warning(
            "Gemini API call failed (%s: %s). Falling back to offline fixture.",
            type(exc).__name__,
            exc,
        )
        return _load_offline_fallback(policy_text)
