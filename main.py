from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from translate import Translator

app = FastAPI()

# Allow requests from your site
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],  # 👈 your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

    translator = Translator(from_lang=source, to_lang=target)
    translated = translator.translate(q)

    return {"translatedText": translated}