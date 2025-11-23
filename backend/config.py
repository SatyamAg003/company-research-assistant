import os
from dotenv import load_dotenv
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY","")
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY","")
BACKEND_HOST = os.getenv("BACKEND_HOST","0.0.0.0")
BACKEND_PORT = int(os.getenv("BACKEND_PORT","8000"))
BACKEND_URL = os.getenv("BACKEND_URL", f"http://{BACKEND_HOST}:{BACKEND_PORT}")