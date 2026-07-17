from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_user
from app import models, schemas

router = APIRouter(prefix="/lessons", tags=["lessons"])

@router.get("", response_model=list[schemas.LessonOut])
def list_lessons(level: str | None = None, db:Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user), ):
    q = db.query(models.Lessons)
    if level:
        q = q.filter(models.Lessons.level == level)
    return q.order_by(models.Lessons.id).all()    

@router.get("/{lesson_id}", response_model=schemas.LessonOut)
def get_lesson(lesson_id: int, db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),):
    lesson = db.query(models.Lessons).get(lesson_id)
    if not lesson:
        raise HTTPException(404, "Lesson not found")
    return lesson

@router.post("/attempt")
def record_attempt(payload: schemas.LessonAttemptCreate, db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),):

    lesson = db.query(models.Lessons).get(payload.lesson_id)
    if not lesson:
        raise HTTPException(404, "Lesson not found")
    
    attempt = models.LessonAttempt(user_id=current_user.id, lesson_id=payload.lesson_id,
        score=payload.score, completed=1 if payload.score >= 70 else 0,)
    
    db.add(attempt)

    if attempt.completed:
        current_user.xp += int(payload.score)

    db.commit()
    return {"recorded": True, "xp": current_user.xp}