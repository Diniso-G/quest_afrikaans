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
        streak=current_user.streak, challenges_com=current_user.challenges_com,
        bugs_fixed=current_user.bugs_fixed, xp_to_next_level=xp_to_next, achievements=[a[0] for a in achievements],)


@router.get("/leaderboard")
def leaderboard(db: Session = Depends(get_db), limit: int = 5):
    top = (db.query(models.User).order_by(models.User.xp.desc()).limit(limit).all())
    return [ {"username": u.username, "xp": u.xp, "level": u.level, "bugs_fixed": u.bugs_fixed}
        for u in top    
    ]
