from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from libretranslatepy import LibreTranslateAPI

# Create FastAPI app
app = FastAPI(title="Translation API")

# Allow requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for testing, allow all origins; change to your frontend in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define request body model
class TranslateRequest(BaseModel):
    q: str
    source: str = "en"
    target: str = "es"

# Initialize LibreTranslate client
lt = LibreTranslateAPI("https://libretranslate.com")  # public instance; change if self-hosted

@app.get("/")
def home():
    return {"message": "Translation API is running"}

@app.get("/translate")
def get_translate_info():
    return {"message": "Use POST with JSON {q, source, target} to translate text"}

@app.post("/translate")
def translate_text(req: TranslateRequest):
    if not req.q:
        raise HTTPException(status_code=400, detail="Missing 'q' field in JSON")

    try:
        translated = lt.translate(req.q, req.source, req.target)
        return {"translatedText": translated}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
