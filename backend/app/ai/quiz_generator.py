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
             "correct_option": "groen", "explanation": "'Groen' means 'green' in Afrikaans"},
        ],
        "en_to_af": [
            {"prompt_text": "dog", "options": ["kat", "hond", "voël", "vis"],
            "correct_option": "hond", "explanation": "'Hond' is Afrikaans for 'dog'."},
        ],
        "af_to_en": [
            {"prompt_text": "huis", "options": ["car", "tree", "house", "book"],
            "correct_option": "house", "explanation": "'Huis' is Afrikaans for 'house'."},
        ],
    },
    "Intermediate": {
        "scenario": [
            {"prompt_text": "What colour is grass?", "options": ["groen", "rooi", "blou", "geel"],
             "correct_option": "groen", "explanation": "'Groen' means 'green' in Afrikaans"},
        ],
        "en_to_af": [
            {"prompt_text": "dog", "options": ["kat", "hond", "voël", "vis"],
            "correct_option": "hond", "explanation": "'Hond' is Afrikaans for 'dog'."},
        ],
        "af_to_en": [
            {"prompt_text": "huis", "options": ["car", "tree", "house", "book"],
            "correct_option": "house", "explanation": "'Huis' is Afrikaans for 'house'."},
        ],
    },
    "Advanced": {
        "scenario": [
            {"prompt_text": "What colour is grass?", "options": ["groen", "rooi", "blou", "geel"],
             "correct_option": "groen", "explanation": "'Groen' means 'green' in Afrikaans"},
        ],
        "en_to_af": [
            {"prompt_text": "dog", "options": ["kat", "hond", "voël", "vis"],
            "correct_option": "hond", "explanation": "'Hond' is Afrikaans for 'dog'."},
        ],
        "af_to_en": [
            {"prompt_text": "huis", "options": ["car", "tree", "house", "book"],
            "correct_option": "house", "explanation": "'Huis' is Afrikaans for 'house'."},
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