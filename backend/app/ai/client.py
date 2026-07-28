from app.config import settings

ai_available = bool(settings.gemenai_api_key)

_client = None
if ai_available:
    from