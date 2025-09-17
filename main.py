from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import logging
import asyncio
from translate import Translator

# -----------------------
# Logging setup
# -----------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("translate_api")

# -----------------------
# FastAPI app
# -----------------------
app = FastAPI(
    title="LibreTranslate API Wrapper",
    description="A FastAPI wrapper for self-hosted LibreTranslate",
    version="1.0.0",
)

# -----------------------
# CORS
# -----------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://contenthub.guru"],  # Change to your frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------
# Request Model
# -----------------------
class TranslateRequest(BaseModel):
    q: str
    source: str = "en"
    target: str = "es"

# -----------------------
# Middleware for logging
# -----------------------
@app.middleware("http")
async def log_requests(request, call_next):
    logger.info(f"Incoming request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")
    return response

# -----------------------
# Health Check
# -----------------------
@app.get("/")
async def home():
    return {"message": "Translation API is running"}

@app.get("/translate")
async def get_translate_info():
    return {"message": "Use POST with JSON to translate text"}

# -----------------------
# Translate Endpoint
# -----------------------
@app.post("/translate")
async def translate_text(data: TranslateRequest):
    if not data.q.strip():
        return JSONResponse(content={"error": "No text provided"}, status_code=400)

    logger.info(f"Translating ({len(data.q)} chars) from {data.source} to {data.target}")

    try:
        # Run blocking translation in executor to avoid blocking event loop
        translated = await asyncio.get_running_loop().run_in_executor(
            None, lambda: Translator(from_lang=data.source, to_lang=data.target).translate(data.q)
        )

        if not translated:
            logger.error("Translation returned empty")
            return JSONResponse(content={"error": "Translation failed"}, status_code=500)

        logger.info(f"Translated text: {translated}")

        return JSONResponse(content={
            "translatedText": translated,
            "source": data.source,
            "target": data.target,
            "length": len(translated)
        })

    except Exception as e:
        logger.exception("Translation failed")
        return JSONResponse(
            content={"error": f"Translation failed: {str(e)}"}, status_code=500
        )


