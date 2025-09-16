from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# CORS middleware — allow all origins temporarily for testing
# You can replace ["*"] with ["https://contenthub.guru"] in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://contenthub.guru"],  # or ["https://contenthub.guru"] for stricter CORS
    allow_credentials=True,
    allow_methods=["*"],  # allow all HTTP methods including POST, OPTIONS
    allow_headers=["*"],  # allow all headers
)

# Logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Incoming request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")
    return response

# Root endpoint
@app.get("/")
def home():
    return {"message": "Translation API is running"}

# Test GET endpoint
@app.get("/translate")
def test_translate():
    return {"message": "Use POST with JSON to translate text"}

# Translation POST endpoint
@app.post("/translate")
async def translate_text(data: dict):
    q = data.get("q")
    if not q:
        return JSONResponse(content={"error": "No text provided"}, status_code=400)

    source = data.get("source", "en")
    target = data.get("target", "es")

    logger.info(f"Translating text ({len(q)} chars) from {source} to {target}")

    try:
        # Call your hosted LibreTranslate API
        res = requests.post(
            "https://translateapi-1-mx67.onrender.com/translate",
            json={"q": q, "source": source, "target": target},
            timeout=20
        )
        res.raise_for_status()
        result = res.json()
        translated = result.get("translatedText")

        if not translated:
            logger.error(f"No translation returned: {result}")
            return JSONResponse(content={"error": "Translation failed"}, status_code=500)

        logger.info(f"Translated text: {translated}")
        return JSONResponse(content={"translatedText": translated})

    except requests.exceptions.RequestException as e:
        logger.error(f"Translation request failed: {e}")
        return JSONResponse(content={"error": f"Translation request failed: {str(e)}"}, status_code=500)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return JSONResponse(content={"error": f"Unexpected error: {str(e)}"}, status_code=500)
