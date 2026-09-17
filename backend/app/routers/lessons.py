from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_user
from app import models, schemas, gamification

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
        score=payload.score, completed=0,)
    
    db.add(attempt)
    db.flush()

    xp_awarded, unlocked = gamification.apply_lesson_result(db, current_user, lesson, payload.score,)

    #print("XP AWARDED: ", xp_awarded)
    #print("USER XP AFTER GAMIFICATION: ", current_user.xp)


    attempt.completed = 1 if xp_awarded > 0 else 0

    #if attempt.completed:
    #    current_user.xp += int(payload.score)

    db.commit()
    #db.refresh(current_user)

    #print("XP AFTER COMMIT: ", current_user.xp)
    #print("STREAK AFTER COMMIT: ", current_user.streak)

    return {"recorded": True, "xp": current_user.xp, "level": current_user.level, "streak": current_user.streak, "unlocked_achievements": unlocked,}

