from fastapi import APIRouter, Depends 
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_user
from app import models, schemas, auth as auth_utils

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=schemas.UserOut)
def get_current_user( current_user: models.User = Depends(auth_utils.get_current_user)):
    return current_user


