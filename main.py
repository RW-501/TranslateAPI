from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from translate import Translator  # pip install translate
import logging

# -----------------------
# Logging setup
# -----------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("translate_api")

# -----------------------
# FastAPI app
# -----------------------
app = FastAPI(
    title="LibreTranslate API Wrapper (No Models)",
    description="A FastAPI wrapper using online translation via 'translate' package",
    version="1.3.0",
)

# -----------------------
# CORS
# -----------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", "https://contenthub.guru"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------
# Defaults
# -----------------------
DEFAULT_SOURCE = "en"
DEFAULT_TARGET = "es"

# -----------------------
# Request Model
# -----------------------
class TranslateRequest(BaseModel):
    q: str
    source: str = DEFAULT_SOURCE
    target: str = DEFAULT_TARGET

# -----------------------
# Health Check
# -----------------------
@app.get("/")
async def home():
    return {
        "message": "Translation API is running",
        "defaults": {"source": DEFAULT_SOURCE, "target": DEFAULT_TARGET},
        "note": "No local models required; uses online translation via 'translate' package"
    }

# -----------------------
# Translate Endpoint (GET)
# -----------------------
@app.get("/translate")
async def translate_text_get(q: str, source: str = DEFAULT_SOURCE, target: str = DEFAULT_TARGET):
    try:
        translator = Translator(from_lang=source, to_lang=target)
        translated = translator.translate(q)
        return {"translatedText": translated, "source": source, "target": target, "length": len(translated)}
    except Exception as e:
        logger.error(e)
        return JSONResponse(
            content={"error": str(e), "defaults": {"source": DEFAULT_SOURCE, "target": DEFAULT_TARGET}},
            status_code=400
        )

# -----------------------
# Translate Endpoint (POST)
# -----------------------
@app.post("/translate")
async def translate_text_post(data: TranslateRequest):
    try:
        translator = Translator(from_lang=data.source, to_lang=data.target)
        translated = translator.translate(data.q)
        return {"translatedText": translated, "source": data.source, "target": data.target, "length": len(translated)}
    except Exception as e:
        logger.error(e)
        return JSONResponse(
            content={"error": str(e), "defaults": {"source": DEFAULT_SOURCE, "target": DEFAULT_TARGET}},
            status_code=400
        )
