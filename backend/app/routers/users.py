from fastapi import APIRouter, Depends 
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_user
from app import models, schemas, auth as auth_utils
from app.gamification import XP_PER_LEVEL

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=schemas.UserOut)
def get_current_user( current_user: models.User = Depends(auth_utils.get_current_user)):
    return current_user

@router.get("/me/dashboard", response_model=schemas.DashboardStats)
def get_dashboard(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    xp_to_next = XP_PER_LEVEL - (current_user.xp % XP_PER_LEVEL)
    achievements = (db.query(models.Achievement.title)
        .join(models.UserAchievement, models.UserAchievement.achievement_id == models.Achievement.id)
        .filter(models. UserAchievement.user_id == current_user.id).all())
    return schemas.DashboardStats(xp=current_user.xp, level=current_user.level,
        streak=current_user.streak, xp_to_next_level=xp_to_next, achievements=[a[0] for a in achievements],)


@router.get("/leaderboard")
def leaderboard(db: Session = Depends(get_db), limit: int = 5):
    top = (db.query(models.User).order_by(models.User.xp.desc()).limit(limit).all())
    return [ {"username": u.username, "xp": u.xp, "level": u.level}
        for u in top    
    ]

@router.get("/me/history", response_model=list[schemas.HistoryItem])
def get_history(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db), limit: int = 200):
    items = []
    lesson_rows = (db.query(models.LessonAttempt, models.Lessons.title).join(models.Lessons, models.Lessons.id == models.LessonAttempt.lesson_id)
        .filter(models.LessonAttempt.user_id == current_user.id).all())

    for attempt, title in lesson_rows:
        items.append(schemas.HistoryItem(type="lesson", label=title, 
            detail=f"Score: {attempt.score}" if attempt.score is not None else None,
            correct=bool(attempt.completed), score=attempt.score, created_at=attempt.created_at))

    quiz_rows = (db.query(models.QuizAttempt, models.Question.prompt_text).join(models.Question, models.Question.id == models.QuizAttempt.question_id)
        .filter(models.QuizAttempt.user_id == current_user.id).all())

    for attempt, prompt in quiz_rows:
        items.append(schemas.HistoryItem(type="quiz", label=prompt, 
            detail=f"You answered: {attempt.selected_option}",
            correct=bool(attempt.is_correct), created_at=attempt.created_at))

    vocab_rows = (db.query(models.VocabAttempt, models.VocabWord.english_word, models.VocabWord.afrikaans_word)
        .join(models.VocabWord, models.VocabWord.id == models.VocabAttempt.word_id)
        .filter(models.VocabAttempt.user_id == current_user.id).all())

    for attempt, eng, af in vocab_rows:
        items.append(schemas.HistoryItem(type="vocab", label=f"{eng} / {af}", 
            detail=f"You answered: {attempt.submitted_answer}",
            correct=bool(attempt.is_correct), score=attempt.similarity, created_at=attempt.created_at))

    pron_rows = (db.query(models.PronounciationAttempt)
        .filter(models.PronounciationAttempt.user_id == current_user.id).all())

    for attempt in pron_rows:
        items.append(schemas.HistoryItem(type="pronunciation", label=attempt.target_phrase, 
            detail=attempt.transcribed_text,
            correct=(attempt.pronounciation_score >= 70) if attempt.pronounciation_score is not None else None, score=attempt.pronounciation_score, created_at=attempt.created_at))

    items.sort(key=lambda i: i.created_at, reverse=True)
    return items[:limit]
    #return [ {"username": u.username, "xp": u.xp, "level": u.level}
  #   for u in top    
   # ]
