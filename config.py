import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    ASSISTANT_NAME = os.getenv("ASSISTANT_NAME", "Nova")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "")
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "5000"))
    MEMORY_FILE = os.getenv("MEMORY_FILE", "memory.json")
    ENABLE_VOICE = os.getenv("ENABLE_VOICE", "false").lower() == "true"
