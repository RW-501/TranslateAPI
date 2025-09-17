from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from translate import Translator
import logging

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Allow requests from your frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://contenthub.guru"],  # Replace with your site
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Incoming request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")
    return response

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
        return JSONResponse(content={"error": "No text provided"}, status_code=400)

    source = data.get("source", "en")
    target = data.get("target", "es")

    logger.info(f"Translating ({len(q)} chars) from {source} to {target}")

    try:
        # Use local translate library
        translator = Translator(from_lang=source, to_lang=target)
        translated = translator.translate(q)

        if not translated:
            logger.error("Translation returned empty")
            return JSONResponse(content={"error": "Translation failed"}, status_code=500)

        logger.info(f"Translated text: {translated}")
        return JSONResponse(content={"translatedText": translated})

    except Exception as e:
        logger.error(f"Translation failed: {e}")
        return JSONResponse(content={"error": f"Translation failed: {str(e)}"}, status_code=500)
