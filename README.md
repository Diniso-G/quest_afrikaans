# Afrikaans Quest Learning
An I/ML-powered Afrikaans language kearning app: lessons, pronounciation scoring, and (planned) proficiency prediction.

## Stack
- FastAPI
- SQLAlchemy (SQLite by default)
- JWT auth on backend
- React + Vite on frontend

## Quick start

### Backend
``` bash
cd backenc
python3- m venv venv && source venv/bin/activate
pip install -r requiremnets.txt
cp .env
uvicorn app.main:app --reload --port 8001
```
Runs at http://localhost:8001 (docs at `/docs`). 


### Frontend
```bash
cd frontend
npm install
cp .env
npm run dev
```

Runs at http://localhost:5173.

## What's implemented
- Auth (register/login, JWT) 




