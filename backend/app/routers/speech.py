import difflib
from fastapi import APIRouter, Depends 
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_user
from app import models, schemas
from app.gamification import XP_PER_LEVEL
from app.ai.client import ai_available, chat

router = APIRouter(prefix="/speech", tags=["speech"])

SYSTEM_PROMPT = """You are an Afrikaans pronounciation couch. You are given a target Afrikaans
phrase and a transcript of what the learner actually said (from speech to text). Score how close 
the transcript is to the target phrase (0-100) accounting for common Afrikaans learner mistakes, 
and give one short, encouraging piece of feedback. Respond with ONLY JSON: {"score": number, "feedback": "...."}
"""

def score_pronounciation(target: str, transcribed: str) -> tuple[float, str]:
    if ai_available:
        import json
        raw = chat(SYSTEM_PROMPT, f"Target: {target}\nTranscript: {transcribed}")
        data = json.loads(raw)
        return float(data.get("score", 0)), data.get("feedback", "")

