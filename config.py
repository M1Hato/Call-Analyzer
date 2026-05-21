from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    GEMINI_API_KEY: str
    GOOGLE_CREDENTIALS_FILE: str = "credentials.json"

    CLIENT_AUDIO: str
    CLIENT_PROCESSED: str
    TABLE: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()