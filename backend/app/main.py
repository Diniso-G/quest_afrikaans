from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base, SessionLocal
from app import models
from app.routers import auth

Base.metadata.create_all(bind=engine)

app = FastAPI( title="QuestAfrikaans", description="Learn Afrikaans proficiency. AI-generated challenges.",
    version="0.1.0",
)
app.add_middleware(CORSMiddleware, allow_origins=["*"],allow_credentials=True,allow_methods=["*"],allow_headers=["*"],)

app.include_router(auth.router)

@app.get("/")
def root():
    return {"status": "ok", "service": "QuestAfrikaans backend"}
