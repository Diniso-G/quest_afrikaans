import difflib
import random

from app import models

VALID_DIRECTIONS = ["en_to_af", "af_to_en"]
VALID_MODES = ["multiple_choice", "free_text"]

FUZZY_MATCH_THRESHOLD = 0.75

def resolve_direction(direction: str) -> str:
    if direction in VALID_DIRECTIONS:
        return direction
    return random.choice(VALID_DIRECTIONS)

def resolve_mode(mode: str) -> str:
    if mode in VALID_MODES:
        return mode
    return random.choice(VALID_MODES)

def prompt_and_answer(word: models.VocabWord, direction:str) -> tuple[str, str]:
    if direction == "en_to_af":
        return word.english_word, word.afrikaans_word
    return word.afrikaans_word, word.english_word

def build_distractors(db, word: models.VocabWord, direction: str, count: int = 3) -> list[str]:
    pool = (db.query(models.VocabWord).filter(models.VocabWord.difficulty == word.difficulty, models.VocabWord.id != word.id).all())

    random.shuffle(pool)
    answer_field = "afrikaans_word" if direction == "en_to_af" else "english_word"
    distractors = []
    for candidate in pool:
        value = getattr(candidate, answer_field)
        if value not in distractors:
            distractors.append(value)
        if len(distractors) >= count:
            break
    return distractors

def is_fuzzy_match(submitted: str, correct: str) -> float:
    return difflib.SequenceMatcher(None, submitted.strip().lower(), correct.strip().lower()).ratio()
