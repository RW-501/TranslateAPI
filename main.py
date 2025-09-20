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
        "http://localhost:3000"
    ],
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
# Health Check
# -----------------------
@app.get("/")
async def home():
    installed_languages = argostranslate.translate.get_installed_languages()
    langs = [f"{lang.code} ({lang.name})" for lang in installed_languages]
    return {"message": "Translation API is running", "languages": langs}

# -----------------------
# Translate Endpoint
# -----------------------
@app.post("/translate")
async def translate_text(data: TranslateRequest):
    if not data.q.strip():
        return JSONResponse(content={"error": "No text provided"}, status_code=400)

    try:
        installed_languages = argostranslate.translate.get_installed_languages()
        from_lang = next((lang for lang in installed_languages if lang.code == data.source), None)
        to_lang = next((lang for lang in installed_languages if lang.code == data.target), None)

        if not from_lang or not to_lang:
            return JSONResponse(
                content={"error": f"Language not supported: {data.source} → {data.target}"},
                status_code=400,
            )

        translated = from_lang.get_translation(to_lang).translate(data.q)

        return {
            "translatedText": translated,
            "source": data.source,
            "target": data.target,
            "length": len(translated)
        }

    except Exception as e:
        logger.exception("Translation failed")
        return JSONResponse(
            content={"error": f"Translation failed: {str(e)}"}, status_code=500
        )
