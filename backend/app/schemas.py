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
    level: int
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

class PronounciationRequest(BaseModel):
    target_phrase: str
    transcribed_text: str

class PronounciationResult(BaseModel):
    pronounciation_score: float
    feedback: str

class DashboardStats(BaseModel):
    xp: int
    level: int
    streak: int
    xp_to_next_level: int
    achievements: List[str]

class QuizGenerateRequest(BaseModel):
    difficulty: str
    question_type: Optional[str] = None

class QuestionOut(BaseModel):
    id: int
    question_type: str
    difficulty: str
    prompt_text: str
    options: List[str]

    class Config:
        from_attributes = True

class QuizAnswerRequest(BaseModel):
    question_id: int
    selected_option: str

class QuizAnswerResult(BaseModel):
    is_correct: bool
    correct_option: str
    explanation: Optional[str]
    xp_awarded: int
    total_xp: int

