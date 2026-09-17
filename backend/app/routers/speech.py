import difflib
import os
import tempfile

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException 
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_user
from app import models, schemas, gamification
from app.gamification import XP_PER_LEVEL
from app.ai.client import ai_available, chat
from app.ai.asr import asr_available, transcribe_audio_file
import json

router = APIRouter(prefix="/speech", tags=["speech"])

SYSTEM_PROMPT = """You are an Afrikaans pronounciation couch. You are given a target Afrikaans
phrase and a transcript of what the learner actually said (from speech to text). Score how close 
the transcript is to the target phrase (0-100) accounting for common Afrikaans learner mistakes, 
and give one short, encouraging piece of feedback IN ENGLISH ONLY. Respond with ONLY JSON: {"score": number, "feedback": "...."}
"""

def score_pronounciation(target: str, transcribed: str) -> tuple[float, str]:
    if ai_available:
        try:
            raw = chat(SYSTEM_PROMPT, f"Target: {target}\nTranscript: {transcribed}", json_mode=True)
            data = json.loads(raw)
            return float(data.get("score", 0)), data.get("feedback", "")
        except Exception:
            pass
            
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
    db.flush()

    gamification.apply_pronounciation_result(db, current_user, score)
    db.commit()

    return schemas.PronounciationResult(pronounciation_score=score, feedback=feedback)

MAX_AUDIO_BYTES = 10 * 1024 * 1024

@router.post("/transcribe", response_model=schemas.TranscriptionResult)
async def transcribe(audio: UploadFile = File(...), current_user: models.User = Depends(get_current_user),):
    if not asr_available:
        raise HTTPException(503, "Speech-to-text isn't set up on this server. Install 'google-genai' "
            "(and the ffmpeg system binary) to enable audio transcription.",)

    contents = await audio.read()
    if len(contents) > MAX_AUDIO_BYTES:
        raise HTTPException(400, "Audio file is too large (max 10MB).")
    if not contents:
        raise HTTPException(400, "Uploaded audio file is empty.")

    suffix = os.path.splitext(audio.filename or "")[1] or ".wav"
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(contents)
            tmp_path = tmp.name

        text = transcribe_audio_file(tmp_path)

    except RuntimeError as e:
        raise HTTPException(503, str(e))
    except Exception:
        raise HTTPException(400, "Couldn't transcribe that audio file - is it a valid audio format?")
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)

    return schemas.TranscriptionResult(transcribed_text=text)

