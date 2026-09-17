import random

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_user
from app import models, schemas, gamification
from app.gamification import XP_BY_DIFFICULTY
from app.ai.quiz_generator import VALID_DIFFICULTIES
from app.vocab_logic import (resolve_direction, resolve_mode, prompt_and_answer, build_distractors, is_fuzzy_match, FUZZY_MATCH_THRESHOLD,)

router = APIRouter(prefix="/vocab", tags=["vocab"])

VALID_DIRECTION_INPUTS = ["en_to_af", "af_to_en", "mixed"]
VALID_MODE_INPUTS = ["multiple_choice", "free_text"]

@router.post("/practice/generate", response_model=schemas.VocabPromptOut)
def generate_practice(payload: schemas.VocabPracticeRequest, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user),):
    if payload.difficulty not in VALID_DIFFICULTIES:
        raise HTTPException(400, f"difficulty must be one of {VALID_DIFFICULTIES}")
    if payload.direction and payload.direction not in VALID_DIRECTION_INPUTS:
        raise HTTPException(400, f"direction must be one of {VALID_DIRECTION_INPUTS}")
    if payload.mode and payload.mode not in VALID_MODE_INPUTS:
        raise HTTPException(400, f"mode must be one of {VALID_MODE_INPUTS}")

    words = db.query(models.VocabWord).filter(models.VocabWord.difficulty == payload.difficulty).all()
    if not words:
        raise HTTPException(404, f"No vocab words seeded for difficulty '{payload.difficulty}'")

    word = random.choice(words)
    direction = resolve_direction(payload.direction or "mixed")
    mode = resolve_mode(payload.mode)

    prompt_word, correct_answer = prompt_and_answer(word, direction)
    options = None
    if mode == "multiple_choice":
        distractors = build_distractors(db, word, direction, count=3)
        options = distractors + [correct_answer]
        random.shuffle(options)

    return schemas.VocabPromptOut(word_id=word.id, difficulty=word.difficulty, direction=direction, mode=mode, prompt_word=prompt_word, options=options,
    )

@router.post("/practice/answer", response_model=schemas.VocabAnswerResult)
def answer_practice(payload: schemas.VocabAnswerRequest, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user),):
    if payload.direction not in ["en_to_af", "af_to_en"]:
        raise HTTPException(400, "direction must be 'en_to_af' or 'af_to_en'")
    if payload.mode not in VALID_MODE_INPUTS:
            raise HTTPException(400, f"mode must be one of {VALID_MODE_INPUTS}")

    word = db.query(models.VocabWord).get(payload.word_id)
    if not word:
        raise HTTPException(404, "Word not found")
    _, correct_answer = prompt_and_answer(word, payload.direction)

    similarity = None
    if payload.mode == "multiple_choice":
        is_correct = payload.answer.strip() == correct_answer.strip()
    else:
        similarity = is_fuzzy_match(payload.answer, correct_answer)
        is_correct = similarity >= FUZZY_MATCH_THRESHOLD
        
    attempt = models.VocabAttempt(user_id=current_user.id, word_id=word.id, 
        direction=payload.direction, mode=payload.mode, submitted_answer=payload.answer,
        is_correct=1 if is_correct else 0, similarity=similarity,)

    db.add(attempt)

    #xp_awarded = 0
    #if is_correct:
    #    xp_awarded = XP_BY_DIFFICULTY.get(word.difficulty, 10)
     #   current_user.xp += xp_awarded

    xp_awarded, unlocked = gamification.apply_vocab_result(db, current_user, word.difficulty, is_correct)

    db.commit()

    return schemas.VocabAnswerResult(
        is_correct=is_correct, correct_answer=correct_answer,
        similarity=similarity, xp_awarded=xp_awarded, total_xp=current_user.xp,
    )
                            
