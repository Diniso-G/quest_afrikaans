from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas, auth as auth_utils


router = APIRouter(prefix="/auth", tags=["auth"])
''''
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    '''

@router.post("/register", response_model=schemas.UserOut, status_code=201)
def register(payload: schemas.UserCreate, db:Session = Depends(get_db)):
    existing = db.query(models.User).filter((models.User.email==payload.email) | (models.User.username == payload.username)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = models.User(email=payload.email, username=payload.username, hashed_password=auth_utils.hash_password(payload.password),)
    db.add(user)
    db.commit()
    db.refresh(user)

    #token = create_access_token({"sub": user.email})
    #return {"access_token": token, "token_type": "bearer"}
    return user

@router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm= Depends(), db:Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email==form_data.username).first()
    if not user or not auth_utils.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = auth_utils.create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}