import json
import random

from fastapi import APIRouter, Depends, HTTPException
from sqlaclchemy.orm import Session

from app.database import get_db
from app.auth import get_current_user
from app import models, schemas
from app.gamification import XP_BY_DIFFICULTY
from app.ai.quiz_generator import generate_question, VALID_DIFFICULTIES, VALID_TYPES

router = APIRouter(prefix="/quiz", tag=["quiz"])

#@router.post("/generate", response_model=schemas.QuestionOut)
