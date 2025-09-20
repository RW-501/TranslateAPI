from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import logging
import argostranslate.translate

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
    description="A FastAPI wrapper using Argos Translate models",
    version="1.3.0",
)

# -----------------------
# CORS
# -----------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://contenthub.guru",
        "https://contenthub.guru/",
        "*"  # 👈 allow all origins for now
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------
# Defaults (always available)
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
    installed_languages = argostranslate.translate.get_installed_languages()
    langs = [f"{lang.code} ({lang.name})" for lang in installed_languages]

    return {
        "message": "Translation API is running",
        "defaults": {"source": DEFAULT_SOURCE, "target": DEFAULT_TARGET},
        "installed_languages": langs
    }

# -----------------------
# Translate Endpoint (GET)
# -----------------------
@app.get("/translate")
async def translate_text_get(q: str, source: str = DEFAULT_SOURCE, target: str = DEFAULT_TARGET):
    installed_languages = argostranslate.translate.get_installed_languages()
    from_lang = next((lang for lang in installed_languages if lang.code == source), None)
    to_lang = next((lang for lang in installed_languages if lang.code == target), None)

    if not from_lang or not to_lang:
        return JSONResponse(
            content={"error": f"Language not supported: {source} → {target}",
                     "defaults": {"source": DEFAULT_SOURCE, "target": DEFAULT_TARGET}},
            status_code=400
        )

    translated = from_lang.get_translation(to_lang).translate(q)

    return {
        "translatedText": translated,
        "source": source,
        "target": target,
        "length": len(translated)
    }

# -----------------------
# Translate Endpoint (POST)
# -----------------------
@app.post("/translate")
async def translate_text_post(data: TranslateRequest):
    installed_languages = argostranslate.translate.get_installed_languages()
    from_lang = next((lang for lang in installed_languages if lang.code == data.source), None)
    to_lang = next((lang for lang in installed_languages if lang.code == data.target), None)

    if not from_lang or not to_lang:
        return JSONResponse(
            content={"error": f"Language not supported: {data.source} → {data.target}",
                     "defaults": {"source": DEFAULT_SOURCE, "target": DEFAULT_TARGET}},
            status_code=400
        )

    translated = from_lang.get_translation(to_lang).translate(data.q)

    return {
        "translatedText": translated,
        "source": data.source,
        "target": data.target,
        "length": len(translated)
    }
