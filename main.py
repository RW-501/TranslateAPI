from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import requests
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
        # Call your hosted API — not yourself!
        response = requests.post(
            "https://translateapi-1-mx67.onrender.com/translate",
            json={"q": q, "source": source, "target": target},
            timeout=20
        )
        response.raise_for_status()
        result = response.json()
        translated = result.get("translatedText")

        if not translated:
            logger.error(f"No translation returned: {result}")
            return JSONResponse(content={"error": "Translation failed"}, status_code=500)

        logger.info(f"Translated text: {translated}")
        return JSONResponse(content={"translatedText": translated})

    except requests.exceptions.RequestException as e:
        logger.error(f"Translation request failed: {e}")
        return JSONResponse(content={"error": f"Translation request failed: {str(e)}"}, status_code=500)
