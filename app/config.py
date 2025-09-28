from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    OCR_LANGS: str = "en"
    CONFIDENCE_THRESHOLD: float = 0.8
    NORMALIZATION_THRESHOLD: float = 0.5


settings = Settings()