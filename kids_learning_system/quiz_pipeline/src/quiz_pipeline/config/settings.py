import os

class Settings:
    QUIZ_PIPELINE_MODE = os.getenv("QUIZ_PIPELINE_MODE", "dev")
    MEDIA_API_KEY = os.getenv("MEDIA_API_KEY", "")

settings = Settings()
