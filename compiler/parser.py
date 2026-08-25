import os
import json
import re
import importlib.util
from typing import Optional
from compiler.ir import WorkflowIR, Step

# Optional local requests for Ollama
import urllib.request
import urllib.error

def parse_policy(natural_language_text: str) -> WorkflowIR:
    """
    Converts natural language policy into structured WorkflowIR.
    Tries in priority order:
      1. Google Gemini API (if GEMINI_API_KEY is configured)
      2. Local Ollama LLM (if running on localhost:11434)
      3. Smart Rule-Based Offline Parser (Zero API key / offline fallback)
    """
    api_key = os.getenv("GEMINI_API_KEY")
    
    # 1. Try Gemini API if key is set
    if api_key:
        try:
            return _parse_with_gemini(natural_language_text, api_key)
        except Exception as e:
            print(f"[Parser] Gemini API call skipped/failed: {e}. Falling back...")

    # 2. Try Local Ollama (Free & Local)
    try:
        ollama_res = _parse_with_ollama(natural_language_text)
        if ollama_res:
            return ollama_res
    except Exception:
        pass

    # 3. Smart Offline Rule-Based Fallback (Zero Dependencies / Zero Setup)
    return _parse_offline_fallback(natural_language_text)

def _parse_with_gemini(text: str, api_key: str) -> WorkflowIR:
    if importlib.util.find_spec("google.generativeai") is None:
        raise ImportError("google-generativeai is not installed.")
    
    genai = importlib.import_module("google.generativeai")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    prompt = f"""
You are an enterprise workflow compiler. Convert the following business policy into a JSON list of steps.
Policy: "{text}"

Output ONLY a JSON object matching this schema:
{{
  "steps": [
    {{
      "id": "unique_step_id",
      "role": "Role (e.g. Employee, IT Manager, Finance, System)",
      "action": "action_name (e.g. request_laptop, approve_laptop, send_notification)",
      "condition": "optional condition string or null",
      "dependencies": ["previous_step_ids"]
    }}
  ]
}}
Do not include markdown or backticks in the response if possible.
"""
    response = model.generate_content(prompt)
    raw_text = response.text.strip()
    raw_text = re.sub(r"^```json\s*", "", raw_text)
    raw_text = re.sub(r"\s*```$", "", raw_text)
    data = json.loads(raw_text)
    return WorkflowIR(**data)

def _parse_with_ollama(text: str) -> Optional[WorkflowIR]:
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": "llama3.2:1b",
        "prompt": f"Convert policy to JSON workflow: {text}",
        "stream": False,
        "format": "json"
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=3) as resp:
        res_data = json.loads(resp.read().decode("utf-8"))
        json_obj = json.loads(res_data["response"])
        if "steps" in json_obj:
            return WorkflowIR(**json_obj)
    return None

def _parse_offline_fallback(text: str) -> WorkflowIR:
    """Deterministic, zero-cost offline parser for demo reliability."""
    lower_text = text.lower()
    steps = []

    # Detect Request
    if "request" in lower_text or "joins" in lower_text or "order" in lower_text:
        steps.append(Step(
            id="request_step",
            role="Employee",
            action="request_laptop",
            dependencies=[]
        ))

    # Detect Manager / IT Approval
    if "approve" in lower_text or "manager" in lower_text:
        prev_dep = [steps[-1].id] if steps else []
        steps.append(Step(
            id="manager_approval",
            role="IT Manager",
            action="approve_laptop",
            condition="budget <= 3000" if "budget" in lower_text or "laptop" in lower_text else None,
            dependencies=prev_dep
        ))

    # Detect Notification / System fulfillment
    prev_dep = [steps[-1].id] if steps else []
    steps.append(Step(
        id="export_data",
        role="System",
        action="send_notification",
        dependencies=prev_dep
    ))

    return WorkflowIR(steps=steps)
