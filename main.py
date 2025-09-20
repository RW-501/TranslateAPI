from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import logging
import asyncio
import argostranslate.package
import argostranslate.translate
import os
import urllib.request
from concurrent.futures import ThreadPoolExecutor

# -----------------------
# Logging setup
# -----------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("translate_api")

# -----------------------
# Models directory
# -----------------------
models_dir = os.path.join(os.getcwd(), "models")
os.makedirs(models_dir, exist_ok=True)

# Thread pool executor for downloads/installations
executor = ThreadPoolExecutor(max_workers=2)

# -----------------------
# FastAPI app
# -----------------------
app = FastAPI(
    title="LibreTranslate API Wrapper",
    description="A FastAPI wrapper using Argos Translate models",
    version="1.2.0",
)

# -----------------------
# CORS
# -----------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://contenthub.guru"],  # adjust for production
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
# Helper functions
# -----------------------
def download_and_install_model(source: str, target: str):
    """
    Downloads and installs an Argos Translate model if missing.
    """
    installed_languages = argostranslate.translate.get_installed_languages()
    from_lang = next((l for l in installed_languages if l.code == source), None)
    if from_lang and any(t.to_lang.code == target for t in from_lang.translations):
        return  # Already installed

    model_filename = f"translate-{source}_{target}.argosmodel"
    model_path = os.path.join(models_dir, model_filename)

    if not os.path.exists(model_path):
        url = f"https://www.argosopentech.com/argospkg/{model_filename}"
        logger.info(f"Downloading model {model_filename} from {url}")
        try:
            urllib.request.urlretrieve(url, model_path)
            logger.info(f"Downloaded model to {model_path}")
        except Exception as e:
            logger.error(f"Failed to download model: {e}")
            raise

    logger.info(f"Installing model {model_path}")
    argostranslate.package.install_from_path(model_path)

async def ensure_model_async(source: str, target: str):
    """
    Ensures the model is installed asynchronously.
    Returns True if model is ready, False if queued for download.
    """
    installed_languages = argostranslate.translate.get_installed_languages()
    from_lang = next((l for l in installed_languages if l.code == source), None)
    if from_lang and any(t.to_lang.code == target for t in from_lang.translations):
        return True  # Already installed

    # Schedule download in background thread
    loop = asyncio.get_running_loop()
    loop.run_in_executor(executor, download_and_install_model, source, target)
    return False  # Model is being downloaded

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

    logger.info(f"Translating ({len(data.q)} chars) from {data.source} to {data.target}")

    try:
        # Ensure model is installed asynchronously
        model_ready = await ensure_model_async(data.source, data.target)
        if not model_ready:
            return JSONResponse(
                content={
                    "error": "Model is being downloaded. Try again in a few seconds.",
                    "source": data.source,
                    "target": data.target,
                },
                status_code=202
            )

        # Refresh installed languages
        installed_languages = argostranslate.translate.get_installed_languages()
        from_lang = next((lang for lang in installed_languages if lang.code == data.source), None)
        to_lang = next((lang for lang in installed_languages if lang.code == data.target), None)

        if not from_lang or not to_lang:
            return JSONResponse(
                content={"error": f"Language not supported: {data.source} → {data.target}"},
                status_code=400,
            )

        # Translation in thread executor
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
