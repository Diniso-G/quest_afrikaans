
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime
from app.config import settings

import os

#DATABASE_URL = "sqlite:///./dashboard.db"
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=connect_args)

print("DATABASE URL:", settings.database_url)
print("DATABASE PATH:", os.path.abspath(engine.url.database))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind = engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

'''
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    reports = relationship("Report", back_populates="owner")

class Report(Base):
    __tablename__ = "reports"
    id = Column(Integer, primary_key=True)
    filename = Column(String)
    total_revenue = Column(Float)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="reports")

Base.metadata.create_all(engine)
'''

