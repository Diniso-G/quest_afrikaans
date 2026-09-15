import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

TARGET_LANGUAGE = "af"
asr_available = True
client = genai.Client(api_key=os.getenv("GEMENAI_API_KEY"))

def transcribe_audio_file(file_path: str) -> str:
    if not os.path.exists(file_path):
        raise RuntimeError(f"Audio file not found: {file_path}")
    try:
        with open(file_path, "rb") as audio_file:
            audio_data = audio_file.read()

        response = client.models.generate_content(model="gemini-2.5-flash", contents=[{"inline_data": {"mime_type": "audio/wav", "data": audio_data,}},
            ],)
        return response.text.strip()
    
    except Exception as e:
        _model_load_error = RuntimeError(f"Gemini transcription failed: {e}")
        raise _model_load_error
    