from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserOut(BaseModel):
    id: int
    email: str
    username: str
    xp: int
    proficiency_level: str
    streak: int
    
    class Config:
        from_attributes = True


class LessonOut(BaseModel):
    id: int
    title: str
    topic: str
    level: str
    content: str
    example_sentences: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class LessonAttemptCreate(BaseModel):
    lesson_id: int
    score: float


class DashboardStats(BaseModel):
    xp: int
    level: int
    streak: int
    challenges_com: int
    bugs_fixed: int
    xp_to_next_level: int
    achievements: List[str]


