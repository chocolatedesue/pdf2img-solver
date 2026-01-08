import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("BASE_URL")
MODEL_NAME = os.getenv("MODEL_NAME", "gemini-3-flash-preview")

if not API_KEY:
    print("Warning: API_KEY not found in .env file.")
