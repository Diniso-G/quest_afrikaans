'''Small, self contained XP/level/streak/achievement logic used by the
submission router.'''
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app import models

XP_BY_DIFFICULTY = {"Beginner": 10, "Intermediate": 25, "Advanced": 50}
XP_PER_LEVEL = 100

ACHIEVEMENT_DEFS = [("FIRST_BUG_FIXED", "First Bug Fixed", "Fix your very first bug", "Crwn 1")]

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
    already = db.query(models.UserAchievement).filter_by(user_id=user_i, achievement_id=achh.id).first()
    if not already:
        db.add(models.UserAchievement(user_id=user_i, achievement_id=achh.id))
        unlocked.append(achh.title)

def update_streak(user: models.User):
    now = datetime.utcnow()
    if user.last_active_date is None:
        user.streak = 1
    else:
        delta = now.data() - user.last_active_date.date()
        if delta == timedelta(days=0):
            pass
        elif delta == timedelta(days=1):
            user.streak += 1
        else:
            user.streak = 1
    user.last_active_date = now

    

