from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from libretranslatepy import LibreTranslateAPI

app = FastAPI()

# Allow all origins for now
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://contenthub.guru"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

lt = LibreTranslateAPI("https://translateapi-1-mx67.onrender.com")  # or your server URL

@app.get("/")
def home():
    return {"message": "Translation API is running"}

@app.get("/translate")
def test_translate():
    return {"message": "Use POST with JSON to translate text"}

@app.post("/translate")
async def translate_text(data: dict):
    q = data.get("q")
    source = data.get("source", "en")
    target = data.get("target", "es")

    translated = lt.translate(q, source, target)
    return {"translatedText": translated}
