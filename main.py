from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import requests
import logging

logging.basicConfig(level=logging.INFO)

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://contenthub.guru"],
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

# Root
@app.get("/")
def home():
    return {"message": "Translation API is running"}

# Test route
@app.get("/translate")
def test_translate():
    return {"message": "Use POST with JSON to translate text"}

# Translation endpoint
@app.post("/translate")
async def translate_text(data: dict):
    q = data.get("q")
    if not q:
        return JSONResponse(content={"error": "No text provided"}, status_code=400)

    source = data.get("source", "en")
    target = data.get("target", "es")

    logging.info(f"Translating text ({len(q)} chars) from {source} to {target}")

    # Call your hosted LibreTranslate API (proxy)
    try:
        res = requests.post(
            "https://translateapi-1-mx67.onrender.com/translate",  # Your server URL
            json={"q": q, "source": source, "target": target},
            timeout=10
        )
        res.raise_for_status()
        result = res.json()
        translated = result.get("translatedText")
        if not translated:
            logging.error(f"No translation returned: {result}")
            return JSONResponse(content={"error": "Translation failed"}, status_code=500)
        logging.info(f"Translated text: {translated}")
        return JSONResponse(content={"translatedText": translated})
    except Exception as e:
        logging.error(f"Translation error: {e}")
        return JSONResponse(content={"error": f"Translation error: {str(e)}"}, status_code=500)
