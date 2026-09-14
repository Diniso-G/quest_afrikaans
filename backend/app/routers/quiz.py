import json
import random

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_user
from app import models, schemas
from app.gamification import XP_BY_DIFFICULTY
from app.ai.quiz_generator import generate_question, VALID_DIFFICULTIES, VALID_TYPES

router = APIRouter(prefix="/quiz", tags=["quiz"])

@router.post("/generate", response_model=schemas.QuestionOut)
def generate(payload: schemas.QuizGenerateRequest, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user),):
    if payload.difficulty not in VALID_DIFFICULTIES:
        raise HTTPException(400, f"difficulty must be one of {VALID_DIFFICULTIES}")
    if payload.question_type and payload.question_type not in VALID_TYPES:
        raise HTTPException(400, f"question_type must be one of {VALID_TYPES}")

    question_type = payload.question_type or random.choice(VALID_TYPES)
    generated = generate_question(payload.difficulty, question_type)

    question = models.Question(question_type=question_type, difficulty=payload.difficulty, prompt_text=generated["prompt_text"],
        options=json.dumps(generated["options"]), correct_option=generated["correct_option"], explanation=generated.get("explanation", ""),
    )

    db.add(question)
    db.commit()
    db.refresh(question)

    return schemas.QuestionOut(id=question.id, question_type=question.question_type, difficulty=question.difficulty,
        prompt_text=question.prompt_text, options=generated["options"],
    )

@router.post("/answer", response_model=schemas.QuizAnswerResult)
def answer(payload: schemas.QuizAnswerRequest, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user),):
    question = db.query(models.Question).get(payload.question_id)
    if not question:
        raise HTTPException(404, "Question not found")

    is_correct = payload.selected_option.strip() == question.correct_option.strip()

    attemp = models.QuizAttempt(user_id=current_user.id, question_id=question.id, 
        selected_option=payload.selected_option, is_correct=1 if is_correct else 0,)

    db.add(attemp)

    xp_awarded = 0
    if is_correct:
        xp_awarded = XP_BY_DIFFICULTY.get(question.difficulty, 10)
        current_user.xp += xp_awarded

    db.commit()

    return schemas.QuizAnswerResult(
        is_correct=is_correct, correct_option=question.correct_option,
        explanation=question.explanation, xp_awarded=xp_awarded, total_xp=current_user.xp,
    )