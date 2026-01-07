import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_BASE_URL = os.getenv("GEMINI_BASE_URL")
MODEL_NAME = os.getenv("MODEL_NAME", "gemini-3-flash-preview")

if not GEMINI_API_KEY:
    print("Warning: GEMINI_API_KEY not found in .env file.")
