from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from libretranslatepy import LibreTranslateAPI
from fastapi.responses import JSONResponse
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)

# Create FastAPI app
app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://contenthub.guru"],  # your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logging.info(f"Incoming request: {request.method} {request.url}")
    logging.info(f"Headers: {request.headers}")
    response = await call_next(request)
    logging.info(f"Response status: {response.status_code}")
    return response

# Routes
@app.get("/")
def home():
    return {"message": "Translation API is running"}

@app.get("/translate")
def test_translate():
    return {"message": "Use POST with JSON to translate text"}

# Use a real LibreTranslate server
lt = LibreTranslateAPI("https://libretranslate.de")  # or https://de.libretranslate.com

def translate_with_logging(q: str, source: str = "en", target: str = "es") -> str | None:
    logging.info(f"Translating text ({len(q)} chars) from {source} to {target}")
    try:
        translated = lt.translate(q, source, target)
        logging.info(f"Translated text: {translated}")
        return translated
    except Exception as e:
        logging.error(f"LibreTranslate error: {e}")
        return None

@app.post("/translate")
async def translate_text(data: dict):
    q = data.get("q")
    if not q:
        return JSONResponse(content={"error": "No text provided"}, status_code=400)

    source = data.get("source", "en")
    target = data.get("target", "es")

    translated = translate_with_logging(q, source, target)
    if not translated:
        return JSONResponse(content={"error": "Translation failed"}, status_code=500)

    return JSONResponse(content={"translatedText": translated})
