import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")
SIMLI_API_KEY = os.getenv("SIMLI_API_KEY")
SIMLI_FACE_ID = os.getenv("SIMLI_FACE_ID", "b9e5fba3-071a-4e35-896e-211c4d6eaa7b")

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
JWT_SECRET = os.getenv("JWT_SECRET", "change-me-in-production")
JWT_ALGORITHM = "HS256"

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is not set")
if not SARVAM_API_KEY:
    raise ValueError("SARVAM_API_KEY is not set")