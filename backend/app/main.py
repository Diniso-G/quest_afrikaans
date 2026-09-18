from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base, SessionLocal
from app import models
from app.gamification import ensure_achievement_defs
from app.routers import auth, users, lessons, speech, quiz, vocab

Base.metadata.create_all(bind=engine)

app = FastAPI( title="QuestAfrikaans", description="Learn Afrikaans proficiency. AI-generated challenges.",
    version="0.1.0",
)
app.add_middleware(CORSMiddleware, allow_origins=["*"],allow_credentials=True,allow_methods=["*"],allow_headers=["*"],)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(lessons.router)
app.include_router(speech.router)
app.include_router(quiz.router)
app.include_router(vocab.router)

def _seed_sample_lessons():
    db = SessionLocal()
    try:
        if db.query(models.Lessons).count() == 0:
            db.add_all([
                models.Lessons(title="Greetings", topic="greetings", level="Beginner", content="Learn the most common Afrikaans greetings and how to introduce yourself.",
                example_sentences="Hallo, hoe gaan dit? | Hello, how are you? \nGoeie môre | Good morning\nAangename kennis | Nice to meet you",),
                models.Lessons(title="Numbers 1- 10", topic="numbers", level="Beginner", content="Counting from een to tien, plus how to ask 'how many?'.",
                example_sentences="een, twee, drie, vier, vyf, ses, sewe, agt, nege, tien | one, two, three, four, five, six, seven, eight, nine, ten \nHoeveel? | How many?",),
                models.Lessons(title="Everyday Conversation", topic="conversation", level="Intermediate", content="Common phrases for small talk, asking for help, and getting around.",
                example_sentences="Waar is die badkamer? | Where is the bathroom? \nEkskuus, kan jy my help? | Excuse me, can you help me? \nHoeveel kos dit? | How much does this cost?",),
                models.Lessons(title="Talking About the Past", topic="grammar", level="Intermediate", content="Afrikaans forms the past tense almost entirely with 'het' plus a 'ge-' prefixed verb.",
                example_sentences="Ek het gisteren gewerk| I worked yesterday \nSy het die boek geless | She read the book \nOns het huis toe gegaan | We went home",),
                models.Lessons(title="Opinions and Debate", topic="conversation", level="Advanced", content="Expressing opinions, agreeing and disagreeing, and giving reasons.",
                example_sentences="Ek ding dit is 'n goeie idee | I think that's a good idea \nEk stem nie saam nie | I don't agree\nDit hang af van die situasie | It depends on the situation",),
                models.Lessons(title="Idioms and Expressions", topic="idioms", level="Advanced", content="Common Afrikaans idioms that don't translate literally.",
                example_sentences="Dis nie my kop se pyn nie | That's not my problem (lit: not my head's pain) \nMoenie se lelik lyk nie | Don't look so upset \nDit kom op dieselfde neer | It amounts to the same thing",
                ),
            ])
            db.commit()
    finally:
        db.close()

def _seed_vocab_words():
    db=SessionLocal()
    try:
        if db.query(models.VocabWord).count() == 0:
            beginner = [
                ("dog", "hond"), ("cat", "kat"), ("house", "huis"), ("water", "water"),
                ("bread", "brood"), ("book", "boek"), ("tree", "boom"), ("sun", "son"),
                ("day", "dag"), ("night", "nag"), ("friend", "viend"), ("school", "skool"),
            ]
            intermediate = [
                ("tired", "moeg"), ("happy", "bly"), ("angry", "kwaad"), ("fast", "vinnig"),
                ("slow", "stadig"), ("to eat", "eet"), ("to sleep", "slaap"), ("to walk", "loop"),
                ("please", "asseblief"), ("thank you", "dankie"), ("expensive", "duur"), ("cheap", "goedkoop"),
            ]
            advanced = [
                ("stubborn", "koppig"), ("to give up", "moed opgee"), ("to apologize", "verskoning vra"), ("achievement", "prestasie"),
                ("responsibility", "verantwoordelikheid"), ("environment", "omgewing"), ("opportunity", "geleentheid"), ("experience", "ervaring"),
                ("independent", "onafhanklik"), ("relationship", "verhouding"), ("challenge", "uitdaging"), ("to negotiate", "onderhandel"),
            ]

            for eng, af in beginner:
                db.add(models.VocabWord(english_word=eng, afrikaans_word=af, difficulty="Beginner"))
            for eng, af in intermediate:
                db.add(models.VocabWord(english_word=eng, afrikaans_word=af, difficulty="Intermediate"))
            for eng, af in advanced:
                db.add(models.VocabWord(english_word=eng, afrikaans_word=af, difficulty="Advanced"))

            db.commit()
    finally:
        db.close()

def _seed_achievemnets():
    db = SessionLocal()
    try:
        ensure_achievement_defs(db)
    finally:
        db.close()

@app.on_event("startup")
def on_startup():
    _seed_sample_lessons()
    _seed_vocab_words()
    _seed_achievemnets()

    
@app.get("/")
def root():
    return {"status": "ok", "service": "QuestAfrikaans backend"}
