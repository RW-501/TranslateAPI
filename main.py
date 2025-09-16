from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from translate import Translator

app = FastAPI()

# Allow requests from your site
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://contenthub.guru"],  # 👈 your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Translator API running"}

@app.post("/translate/")
def translate_text(text: str, to_lang: str = "es"):
    translator = Translator(to_lang=to_lang)
    return {"translated": translator.translate(text)}
