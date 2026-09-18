from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "sqlite:///./afrikaans.db"
    secret_key: str = ""
    access_token_expire_minutes: int = 1440
    gemenai_api_key: str = "" #add later and Hide from github
    gemenai_model: str = "gemini-2.5-flash"

    class Config:
        env_file = ".env"

settings = Settings()

if not settings.secret_key:
    raise RuntimeError("SECRET_KEY is not set. Add SECRET_KEY=<a long random string> to your .env file in backend/ before starting the app.")