from fastapi import FastAPI
from translate import Translator

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Translator API running"}

@app.post("/translate/")
def translate_text(text: str, to_lang: str = "es"):
    translator = Translator(to_lang=to_lang)
    return {"translated": translator.translate(text)}
