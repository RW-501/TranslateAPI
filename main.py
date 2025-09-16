from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from libretranslatepy import LibreTranslateAPI
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)

# Create FastAPI app
app = FastAPI()

# Logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logging.info(f"Incoming request: {request.method} {request.url}")
    logging.info(f"Headers: {request.headers}")
    response = await call_next(request)
    logging.info(f"Response status: {response.status_code}")
    return response

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://contenthub.guru"],  # your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Use a real LibreTranslate server
lt = LibreTranslateAPI("https://de.libretranslate.com/")  # ← fix here

# Routes
@app.get("/")
def home():
    return {"message": "Translation API is running"}

@app.get("/translate")
def test_translate():
    return {"message": "Use POST with JSON to translate text"}

@app.post("/translate")
async def translate_text(data: dict):
    q = data.get("q")
    if not q:
        return {"error": "No text provided"}

    source = data.get("source", "en")
    target = data.get("target", "es")

    try:
        # Translate text via LibreTranslate server
        translated = lt.translate(q, source, target)
    except Exception as e:
        return {"error": str(e)}

    return {"translatedText": translated}
