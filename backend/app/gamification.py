'''Small, self contained XP/level/streak/achievement logic used by the
submission router.'''
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app import models

XP_BY_DIFFICULTY = {"Beginner": 10, "Intermediate": 25, "Advanced": 50}
XP_PER_LEVEL = 100

ACHIEVEMENT_DEFS = [
    ("FIRST_LESSON", "First lesson", "Complete your first Afrikaans lesson", "Crwn 1"),
    ("AFRIKAANS_ROOKIE", "Afrikaans Rookie", "Complete 100 learning activities", "Crwn 1"),
    ("AFRIKAANS_ENDURER", "Afrikaans Endurer", "Maintain a learning streak", "Crwn 1"),
    ("AFRIKAANS_AVERAGE_SPEAKER", "Average Speaker", "Reach an average speaking level", "Crwn 1"),
    ("AFRIKAANS_EXPERT", "Afrikaans Experts", "Reach expert level", "Crwn 1"),
    ("STREAK_30", "30-Day Streak", "Maintain a 30 day learning streak", "Crwn 1"),
    
    ]

def ensure_achievement_defs(db: Session):
    '''Seed the achievement table'''
    for code, title, desc, icon in ACHIEVEMENT_DEFS:
        exists = db.query(models.Achievement).filter_by(code=code).first()
        if not exists:
            db.add(models.Achievement(code=code, title=title, description=desc, icon=icon))

    db.commit()

def _award(db: Session, user:models.User, code:str, unlocked: list):
    achh = db.query(models.Achievement).filter_by(code=code).first()
    if not achh:
        return
    already = db.query(models.UserAchievement).filter_by(user_id=user.id, achievement_id=achh.id).first()
    if not already:
        db.add(models.UserAchievement(user_id=user.id, achievement_id=achh.id))
        unlocked.append(achh.title)

def update_streak(user: models.User):
    now = datetime.utcnow()
    if user.last_active_date is None:
        user.streak = 1
    else:
        delta = now.date() - user.last_active_date.date()
        if delta == timedelta(days=0):
            pass
        elif delta == timedelta(days=1):
            user.streak += 1
        else:
            user.streak = 1
    user.last_active_date = now

def check_common_achievements(db: Session, user: models.User, unlocked: list,):

    lesson_cnt = (db.query(models.LessonAttempt).filter(models.LessonAttempt.user_id == user.id, models.LessonAttempt.completed == 1,).count())
    quiz_cnt = (db.query(models.QuizAttempt).filter(models.QuizAttempt.user_id == user.id,).count())
    vocab_cnt = (db.query(models.VocabAttempt).filter(models.VocabAttempt.user_id == user.id,).count())
    pronounciation_cnt = (db.query(models.PronounciationAttempt).filter(models.PronounciationAttempt.user_id == user.id,).count())

    total_activities = (lesson_cnt + quiz_cnt + vocab_cnt + pronounciation_cnt)

    if total_activities >= 100:
        _award(db, user, "AFRIKAANS_ROOKIE", unlocked,)

    if user.streak >= 7:
        _award(db, user, "AFRIKAANS_ENDURER", unlocked,)    
    if user.streak >= 30:
        _award(db, user, "STREAK_30", unlocked,)

    if user.level >= 10:
        _award(db, user, "AFRIKAANS_EXPERT", unlocked,)
    
def apply_lesson_result(
    db: Session, 
    user: models.User, 
    lesson: models.Lessons, 
    score: float,
) -> tuple[int, list]:
    unlocked: list[str] = []
    xp_awarded = 0 

    if score >= 50:
        difficulty = getattr(lesson, "level", "Beginner",)
        base_xp = XP_BY_DIFFICULTY.get(difficulty, 10)
        #penalty = min(hints_used, 3) * 0.15
        #xp_awarded = max(1, round(base_xp * (1 - penalty)))
        xp_awarded = base_xp

        user.xp += xp_awarded
        user.level = (user.xp // XP_PER_LEVEL) + 1
        update_streak(user)
        _award(db, user, "FIRST_LESSON", unlocked,)

        check_common_achievements(
            db, user, unlocked,
        )
    db.commit()
    return xp_awarded, unlocked

def apply_quiz_result(
    db: Session, 
    user: models.User, 
    difficulty: str, 
    is_correct: bool,
) -> tuple[int, list]:
    unlocked: list[str] = []
    xp_awarded = 0 

    if is_correct:
        xp_awarded = XP_BY_DIFFICULTY.get(difficulty, 10,)
        user.xp += xp_awarded
        user.level = (user.xp // XP_PER_LEVEL) + 1

        update_streak(user)
        check_common_achievements(db, user, unlocked,)

    db.commit()

    return xp_awarded, unlocked

def apply_vocab_result(
    db: Session, 
    user: models.User, 
    difficulty: str, 
    is_correct: bool,
) -> tuple[int, list]:
    unlocked: list[str] = []
    xp_awarded = 0 

    if is_correct:
        xp_awarded = XP_BY_DIFFICULTY.get(difficulty, 10,)
        user.xp += xp_awarded
        user.level = (user.xp // XP_PER_LEVEL) + 1

        update_streak(user)
        check_common_achievements(db, user, unlocked,)

    db.commit()

    return xp_awarded, unlocked

def apply_pronounciation_result(
    db: Session, 
    user: models.User, 
    score: float,
) -> tuple[int, list]:
    unlocked: list[str] = []

    if score >= 90:
        xp_awarded = 30
    elif score >= 75:
        xp_awarded = 20
    elif score >= 50:
        xp_awarded = 10
    else:
        xp_awarded = 5

    user.xp += xp_awarded
    user.level = (user.xp // XP_PER_LEVEL) + 1

    update_streak(user)

    average_score = (db.query(models.PronounciationAttempt).filter(models.PronounciationAttempt.user_id == user.id, models.PronounciationAttempt.pronounciation_score.isnot(None),).with_entities(models.PronounciationAttempt.pronounciation_score).all())

    if average_score:
        average = sum(row[0] for row in average_score) / len(average_score)
        if score >= 70:
            _award(db, user, "AFRIKAANS_AVERAGE_SPEAKER", unlocked,)
    check_common_achievements(db, user, unlocked,)

    db.commit()

    return xp_awarded, unlocked

''''
        if user.streak >= 30:
            _award(db, user, "STREAK_30", unlocked)
        if user.level >=10:
            _award(db, user, "AFRIKAANS_", unlocked)
        if user.streak >=30:
            _award(db, user, "STREAK_30", unlocked)
        if challenge.difficulty == "Advanced":
            _award(db, user, "DEBUGGING_EXPERT", unlocked)

        if challenge.language.lower() == "sql":
            sql_solved = (
                db.query(models.Submission).join(models.Challenges).
                filter(models.Submission.user_id == user.id,
                    models.Submisson.is_correct ==True,
                    models.Challenges.language == "SQL",).count()
            )
            if sql_solved >= 10:
                _award(db, user, "SQL_MASTER", unlocked)

        if challenge.language.lower() == "python":
            py_solved = (
                db.query(models.Submission).join(models.Challenges).
                filter(models.Submission.user_id == user.id,
                    models.Submission.is_correct ==True,
                    models.Challenges.language == "Python",).count()
            )
            if py_solved >= 10:
                _award(db, user, "PYTHON_DETECTIVE", unlocked)

    db.commit()
    return xp_awarded, unlocked '''

