"""Hybrid validation helpers for farmer advisory queries."""

import json
import re
import unicodedata

try:
    from google import genai
    from google.genai import types
except ImportError:  # pragma: no cover - handled at runtime in Streamlit
    genai = None
    types = None


MIN_QUERY_LENGTH = 15

GREETING_QUERIES = {
    "hi",
    "hello",
    "hey",
    "how are you",
    "good morning",
}

TRIVIAL_QUERIES = {
    "tell me a joke",
    "python",
    "123456",
    "123456789",
    "abcdef",
    "qwerty",
}

INTENT_CLASSIFIER_PROMPT = """You are an agricultural intent classifier.

Determine whether the user's message is requesting agricultural advice.

Return ONLY valid JSON in this format:

{
  "status": "VALID"
}

or

{
  "status": "INVALID",
  "reason": "The query is not related to agriculture."
}

Return VALID only if the user is genuinely requesting advice related to:

* Crops
* Farming
* Irrigation
* Fertilizers
* Weather
* Harvesting
* Plant diseases
* Pests
* Soil
* Agricultural markets

Return INVALID for:

* Greetings
* Casual conversation
* Personal introductions
* Programming questions
* Jokes
* Sports
* Politics
* General knowledge
* Any non-agricultural topic.

User message:
{advisory_text}
"""


def _normalize(value: str) -> str:
    """Normalize spacing, Unicode variants, and letter case for comparison."""
    normalized = unicodedata.normalize("NFKC", value or "").casefold()
    return " ".join(normalized.split())


def clean_advisory_text(value: str) -> str:
    """Trim and normalize user advisory text without changing its meaning."""
    return " ".join(unicodedata.normalize("NFKC", value or "").strip().split())


def passes_rule_based_validation(value: str) -> bool:
    """Reject obviously invalid advisory input before any AI call is made."""
    query = _normalize(value)
    if not query or len(query) < MIN_QUERY_LENGTH:
        return False

    if query in GREETING_QUERIES or query in TRIVIAL_QUERIES:
        return False

    compact = re.sub(r"\s+", "", query)
    if compact and len(set(compact)) == 1:
        return False

    if compact in TRIVIAL_QUERIES:
        return False

    if not any(ch.isalpha() for ch in query):
        return False

    return True


def _extract_json_object(text: str) -> dict:
    """Parse the first JSON object from a Gemini response."""
    cleaned = (text or "").strip()
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", cleaned, flags=re.IGNORECASE)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
        if not match:
            return {}
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            return {}


def classify_agricultural_intent(advisory_text: str, api_key: str, model: str = "gemini-2.5-flash") -> tuple[bool, str]:
    """Use Gemini to decide whether the advisory text is genuinely agricultural."""
    if genai is None:
        return False, "Gemini SDK is not available."
    if not api_key:
        return False, "Gemini API key is missing."

    client = genai.Client(api_key=api_key)
    prompt = INTENT_CLASSIFIER_PROMPT.format(advisory_text=advisory_text)
    request = {
        "model": model,
        "contents": prompt,
    }
    if types is not None:
        request["config"] = types.GenerateContentConfig(
            temperature=0,
            response_mime_type="application/json",
        )

    try:
        response = client.models.generate_content(**request)
    except Exception as exc:  # pragma: no cover - depends on external Gemini service
        return False, f"Gemini intent classification failed: {exc}"

    payload = _extract_json_object(getattr(response, "text", ""))
    status = str(payload.get("status", "")).strip().upper()
    return status == "VALID", str(payload.get("reason", ""))
