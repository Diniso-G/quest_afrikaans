from app.config import settings

ai_available = bool(settings.gemenai_api_key)

_client = None
if ai_available:
    from google import genai

    _client = genai.Client(api_key=settings.gemenai_api_key)

def chat(system_prompt: str, user_prompt: str, json_mode: bool = False) -> str:
    """Call Gemini and return the raw text response."""
    if not ai_available:
        raise RuntimeError("GEMINI_API_KEY not configured")
    if json_mode:
        system_prompt += ("\nRespond ONLY with valid JSON. Do not use markdown or code fences.")
    prompt = f"""
System:
{system_prompt}

User:
{user_prompt}
"""

    response = _client.models.generate_content(model=settings.gemenai_model, contents=prompt,)

    return response.text