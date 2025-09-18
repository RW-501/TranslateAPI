from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import logging
import asyncio
import argostranslate.package
import argostranslate.translate
import os

# -----------------------
# Logging setup
# -----------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("translate_api")

# -----------------------
# Load Argos Translate models
# -----------------------
models_dir = os.path.join(os.getcwd(), "models")
for filename in os.listdir(models_dir):
    if filename.endswith(".argosmodel"):
        package_path = os.path.join(models_dir, filename)
        logger.info(f"Loading model: {package_path}")
        argostranslate.package.install_from_path(package_path)

installed_languages = argostranslate.translate.get_installed_languages()
print([(lang.code, lang.name) for lang in installed_languages])

# -----------------------
# FastAPI app
# -----------------------
app = FastAPI(
    title="LibreTranslate API Wrapper",
    description="A FastAPI wrapper using Argos Translate models",
    version="1.1.0",
)

# -----------------------
# CORS
# -----------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://contenthub.guru"],  # adjust for prod
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
    langs = [f"{lang.code} ({lang.name})" for lang in installed_languages]
    return {"message": "Translation API is running", "languages": langs}

# -----------------------
# Translate Endpoint
# -----------------------
@app.post("/translate")
async def translate_text(data: TranslateRequest):
    if not data.q.strip():
        return JSONResponse(content={"error": "No text provided"}, status_code=400)

    logger.info(f"Translating ({len(data.q)} chars) from {data.source} to {data.target}")

    try:
        # Find matching installed languages
        from_lang = next((lang for lang in installed_languages if lang.code == data.source), None)
        to_lang = next((lang for lang in installed_languages if lang.code == data.target), None)

        if not from_lang or not to_lang:
            return JSONResponse(
                content={"error": f"Language not supported: {data.source} → {data.target}"},
                status_code=400,
            )

        # Translation is synchronous → run in executor
        translated = await asyncio.get_running_loop().run_in_executor(
            None, lambda: from_lang.get_translation(to_lang).translate(data.q)
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
