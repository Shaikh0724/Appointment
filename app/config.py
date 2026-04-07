import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    MONGODB_URI: str = os.getenv("MONGODB_URI", "")
    SMTP_EMAIL: str = os.getenv("SMTP_EMAIL", "")
    SMTP_APP_PASSWORD: str = os.getenv("SMTP_APP_PASSWORD", "")
    CLINIC_EMAIL: str = os.getenv("CLINIC_EMAIL", "samantha@absjacksonvillenc.com")
    DB_NAME: str = "smilebot"


settings = Settings()
