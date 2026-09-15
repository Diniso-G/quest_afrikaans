import json
import random

from app.ai.client import ai_available, chat

VALID_TYPES= ["scenario", "en_to_af", "af_to_en"]
VALID_DIFFICULTIES = ["Beginner", "Intermediate", "Advanced"]

SYSTEM_PROMPT = """You are an Afrikaans language quiz question writer for a language-learning app.
Generate ONE multiple-choice question for an Englisg-speaking learner of Afrikaans.

Question type meanings:
- "scenario": describe a situation or ask a question in English; the answer options are Afrikaans words/phrases.
- "en_to_af": show an English word or short phrase; the answer options are Afrikaans translations.
- "af_to_en": show an Afrikaans word or short phrase; the answer options are English translations.

Difficulty guidance:
- Beginner: single commone words, with options that are obviously different from each other.
- Intermediate: short phrases, with 1-2 distractor options that are plausable near-misses (similar sounding or similar meaning),
- Advanced: idioms or context-dependent word choice, sentence-level translation, with subtle distractors.

Respond with ONLY JSON in this exact shape, no markdown or commentary:
{"prompt_text": "...", "options": ["...", "...", "...", "..."], "correct_option": "...", "explanation": "..."}

Rules: options must have 3 or 4 entries. correct_option must be one of the strings in options, copied exactly.
explanation should be one short sentence in English. 
"""

OFFLINE_BANK = {
    "Beginner": {
        "scenario": [
            {"prompt_text": "What colour is grass?", "options": ["groen", "rooi", "blou", "geel"],
             "correct_option": "groen", "explanation": "'Groen' means 'green' in Afrikaans."},
            {"prompt_text": "Which word means 'good morning?", "options": ["Goeie môre", "Totsiens", "Asseblief", "Dankie"],
             "correct_option": "Goeie môre", "explanation": "'Goeie môre' is the Afrikaans greeting for 'good morning'."},
        ],
        "en_to_af": [
            {"prompt_text": "dog", "options": ["kat", "hond", "voël", "vis"],
            "correct_option": "hond", "explanation": "'Hond' is Afrikaans for 'dog'."},
            {"prompt_text": "water", "options": ["brood", "melk", "water", "vleis"],
             "correct_option": "water", "explanation": "'Water' is spelled the same in Afrikaans and English."},
        ],
        "af_to_en": [
            {"prompt_text": "huis", "options": ["car", "tree", "house", "book"],
            "correct_option": "house", "explanation": "'Huis' is Afrikaans for 'house'."},
            {"prompt_text": "kat", "options": ["dog", "bird", "fish", "cat"],
             "correct_option": "cat", "explanation": "'Kat' means 'cat'."},
        ],
    },
    "Intermediate": {
        "scenario": [
            {"prompt_text": "What do you say to thank someone?", "options": ["asseblief", "dankie", "totsiens", "jammer"],
             "correct_option": "dankie", "explanation": "'Dankie' means 'thank you' the others mean please, goodbye and sorry."},
            {"prompt_text": "Which word means 'please'?", "options": ["asseblief", "dankie", "welkom", "jammer"],
             "correct_option": "asseblief", "explanation": "'Asseblief' means 'please' in Afrikaans."},
        ],
        "en_to_af": [
            {"prompt_text": "to eat", "options": ["drink", "loop", "eet", "slaap"],
            "correct_option": "eet", "explanation": "'Eat' means 'to eat'; the distractors mean drink, walk and sleep."},
            {"prompt_text": "tired", "options": ["bly", "kwaad", "koud", "moeg"],
             "correct_option": "moeg", "explanation": "'Moeg' means 'tired'."},
        ],
        "af_to_en": [
            {"prompt_text": "warm", "options": ["cold", "wet", "warm", "hard"],
            "correct_option": "moeg", "explanation": "'Moeg' means 'warm' in English too."},
            {"prompt_text": "vinnig", "options": ["fast", "slow", "heavy", "quiet"],
             "correct_option": "fast", "explanation": "'Vinnig' means 'fast'."},
        ],
    },
    "Advanced": {
        "scenario": [
            {"prompt_text": "Which idiom means 'to give up'?", "options": ["trek ann een kant", "slaan die spyker op die kop", "gooi die tou op", "loop met die hoenders"],
             "correct_option": "gooi die tou op", "explanation": "'Gooi die tou op' literally means 'throw the rope up' in Afrikaans and idiomatically means 'to give up'."},
        ],
        "en_to_af": [
            {"prompt_text": "It's raining cats and dogs.", "options": ["Dit reën katte en honde.", "Dit is baie warm buite.", "Die son skyn helder.", "Dit reën ou vroue met knopkieries."],
            "correct_option": "Dit reën ou vroue met knopkieries.", "explanation": "Afrikaans has its own idiom for heavy rain rather than a literal translation."},
        ],
        "af_to_en": [
            {"prompt_text": "Sy is op haar perdjie", "options": ["She is being stubborn/arrogant.", "She is riding a horse.", "She is very happy.", "She is sleeping."],
            "correct_option": "She is being stubborn/arrogant.", "explanation": "This idiom literally means 'she is on her little horse' but is used to mean she's acting high and mighty."},
        ],
    },
}

def _offline_question(difficulty:str, question_type:str) -> dict:
    bank = OFFLINE_BANK.get(difficulty, OFFLINE_BANK["Beginner"])
    choices = bank.get(question_type, bank.get("scenario"))
    return random.choice(choices)

def _valid(data: dict) -> bool:
    if not isinstance(data, dict):
        return False
    options = data.get("options")
    if not isinstance(options, list) or not (3 <= len(options) <= 4):
        return False
    if data.get("correct_option") not in options:
        return False
    if not data.get("prompt_text"):
        return False
    return True

def generate_question(difficulty: str, question_type: str) -> dict:
    """Returns a dict with prompt_text, options (list[str])"""

    if difficulty not in VALID_DIFFICULTIES:
        difficulty = "Beginner"
    if question_type not in VALID_TYPES:
        question_type = random.choice(VALID_TYPES)

    if ai_available:
        try:
            raw = chat(SYSTEM_PROMPT, f"Difficulty: {difficulty}\nQuestion type: {question_type}", json_mode=True,)
            data = json.loads(raw)
            if _valid(data):
                return {
                    "prompt_text": data["prompt_text"], "options": data["options"],
                    "correct_option": data["correct_option"], "explanation": data.get("explanation", ''),
                }
        except Exception:
            pass

    return _offline_question(difficulty, question_type)