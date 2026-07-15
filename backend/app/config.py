from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "sqlite:///./afrikaans.db"
    secret_key: str = "dev-secret_will_change"
    access_token_expire_minutes: int = 1440
    gemenai_api_key: str = " " #add later and Hide from github
    gemenai_model: str = " "

    class Config:
        env_file = ".env"

settings = Settings()