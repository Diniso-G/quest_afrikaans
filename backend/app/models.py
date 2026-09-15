from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    #reports = relationship("Report", back_populates="owner")

    xp = Column(Integer, default= 0)
    level = Column(Integer, default= 1)
    streak = Column(Integer, default= 0)
    last_active_date = Column(DateTime, nullable= True)

    #submissions = relationship("Submission", back_populates="user") 
    achievements = relationship("UserAchievement", back_populates="user")
    lesson_attempts = relationship("LessonAttempt", back_populates="user")
    pronounciation_attempts = relationship("PronounciationAttempt", back_populates="user")
    quiz_attempts = relationship("QuizAttempt", back_populates="user")
    vocab_attempts = relationship("VocabAttempt", back_populates="user")

class Lessons(Base):
    __tablename__ = "lessons"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    topic = Column(String, nullable=False)
    level = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    example_sentences = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    #submissions = relationship("Submission", back_populates="user") 

    attempts = relationship("LessonAttempt", back_populates="lesson")

class LessonAttempt(Base):
    __tablename__ = "lesson_attempts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False)
    score = Column(Float, nullable=True)
    completed = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="lesson_attempts")
    lesson = relationship("Lessons", back_populates="attempts")

class PronounciationAttempt(Base):
    __tablename__ = "pronounciation_attempts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    target_phrase = Column(String, nullable=False)
    transcribed_text = Column(String, nullable=True) 
    pronounciation_score = Column(Float, nullable=True)
    feedback = Column(Text, nullable=True)     
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="pronounciation_attempts")

class Achievement(Base):
    __tablename__ = "achievements"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    icon = Column(String, default="CRWN")

class UserAchievement(Base):
    __tablename__ = "user_achievements"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    achievement_id = Column(Integer, ForeignKey("achievements.id"),nullable=False)
    earned_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="achievements")
    achievement= relationship("Achievement")
    
class Question(Base):
    __tablename__ = "questions" 

    id = Column(Integer, primary_key=True, index=True)
    question_type = Column(String, nullable=False)
    difficulty = Column(String, nullable=False)
    prompt_text = Column(Text, nullable=False)
    options = Column(Text, nullable=False)
    correct_option = Column(String, nullable=False)
    explanation = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    attempts = relationship("QuizAttempt", back_populates="question")
    
class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    selected_option = Column(String, nullable=False) 
    is_correct = Column(Integer, default=0)    
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="quiz_attempts")
    question = relationship("Question", back_populates="attempts")

class VocabWord(Base):
    __tablename__ = "vocab_words"

    id = Column(Integer, primary_key=True, index=True)
    english_word = Column(String, nullable=False)
    afrikaans_word = Column(String, nullable=False) 
    difficulty = Column(String, nullable=False)    
    created_at = Column(DateTime, default=datetime.utcnow)

    attempts = relationship("VocabAttempt", back_populates="word")

class VocabAttempt(Base):
    __tablename__ = "vocab_attempts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    word_id = Column(Integer, ForeignKey("vocab_words.id"), nullable=False)
    direction = Column(String, nullable=False) 
    mode = Column(String, nullable=False)
    submitted_answer = Column(String, nullable=False)
    is_correct = Column(Integer, default=0)  
    similarity = Column(Float, nullable=True)  
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="vocab_attempts")
    word = relationship("VocabWord", back_populates="attempts")
