import difflib
from fastapi import APIRouter, Depends 
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_user
from app import models, schemas
from app.gamification import XP_PER_LEVEL
from app.ai.client import ai_available, chat
import json

router = APIRouter(prefix="/speech", tags=["speech"])

SYSTEM_PROMPT = """You are an Afrikaans pronounciation couch. You are given a target Afrikaans
phrase and a transcript of what the learner actually said (from speech to text). Score how close 
the transcript is to the target phrase (0-100) accounting for common Afrikaans learner mistakes, 
and give one short, encouraging piece of feedback IN ENGLISH ONLY. Respond with ONLY JSON: {"score": number, "feedback": "...."}
"""

def score_pronounciation(target: str, transcribed: str) -> tuple[float, str]:
    if ai_available:
        raw = chat(SYSTEM_PROMPT, f"Target: {target}\nTranscript: {transcribed}", json_mode=True)
        data = json.loads(raw)
        return float(data.get("score", 0)), data.get("feedback", "")

    ratio = difflib.SequenceMatcher(None, target.lower().strip(), transcribed.lower().strip()).ratio()
    score = round(ratio * 100, 1)
    if score >= 85:
        feedback = "Great match - match your pronouciation transcript lines up closely with the target phrase."
    elif score >= 60:
        feedback = "Close! A few sounds are off- listen to the target phrase again and try once more." 
    else:
        feedback = "Not quiet there yet- try breaking the phrase into smaller chunks and repeat each one." 
    return score, feedback

@router.post("/score", response_model=schemas.PronounciationResult)
def score_attempt(payload: schemas.PronounciationRequest, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user),):
    score, feedback = score_pronounciation(payload.target_phrase, payload.transcribed_text)

    attempt = models.PronounciationAttempt(user_id=current_user.id, target_phrase=payload.target_phrase, transcribed_text=payload.transcribed_text, pronounciation_score=score, feedback=feedback,)

    db.add(attempt)
    db.commit()

    return schemas.PronounciationResult(pronounciation_score=score, feedback=feedback)

