# Afrikaans Quest Learning
An AI/ML-powered Afrikaans language kearning app: lessons, pronounciation scoring, and (planned) proficiency prediction.

## Stack
- FastAPI
- SQLAlchemy (SQLite by default)
- JWT auth on backend
- React + Vite on frontend
- Google Gemini for ai generated quiz questions and pronouciation scoring transcription with offline feature

## Quick start

### Backend
``` bash
cd backend
python3- m venv venv && source venv/bin/activate
pip install -r requiremnets.txt
cp .env
uvicorn app.main:app --reload --port 8001

OR

cd backend
python -m venv venv 
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt 
uvicorn app.main:app 
```
Runs at http://localhost:8000 (docs at `/docs`). 


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
- Lessons: browse by level, practice example sentences by typing or recording, get scored
- Quiz: AI generated multiple choice questions with an offline fallback question bank, three difficulties, XP on correct answer
- Word Match: vocab drilling both directions (English and Afrikaans), multiple choice  or free text with fuzzy matching
- Pronunciation practice: type or record a phrase, get scored via Gemini with feedback
- Voice transcription via Gemini
- Gamification: XP, levels, streaks, and achievements, awarded from lessons, quiz, vocab, and pronunciation practice
- Leaderboard(top users by XP)
- Dashboard: XP, level, streak and earned achievements


## ML pronunciation model (in progress)

Exploring a self-traned pronuciation model (MFCC/pitch features + scikit-learn) to eventually sit alongside/ replace the current setup. Training scrips live outside this repo in a separate `pronunciation-ml-experiment/` project- not commited here.

**Data**: NCHLT Afrikaans Speech Corpus (Barnard, Davel, van Heerden, de Wet & Badenhorst, 2014), CC BY 3.0 - https://repo.sadilar.org/items/2bf723bc-7420-439e-a55d-833e10b0c776

### Notes for self
- License requires attribution (this note is that attribution) but does **not** require this project or any model trained on it to be open-sourced.

- The raw corpus (4.5GB) is **not** commited to this repo- keep it in the separate experiment folder only.

- Known intergration gap: `/speech/score` currently only recieves text (`target_phrase`, `transcribed_text`), not audio - recorded clips is discarded right after `/speech/transcribe`. Using an acostic model in production requires changing the flow first.




