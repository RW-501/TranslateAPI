import os
import argostranslate.package
import argostranslate.translate

# Path to your models folder
models_folder = r"C:\Users\lilro\LibreTranslate\models"

# Install all .argosmodel files
for model_file in os.listdir(models_folder):
    if model_file.endswith(".argosmodel"):
        argostranslate.package.install_from_path(os.path.join(models_folder, model_file))

# List installed languages
installed_languages = argostranslate.translate.get_installed_languages()
for lang in installed_languages:
    print(lang.name, lang.code)

# Translate English → Spanish
from_lang = next(l for l in installed_languages if l.code == "en")
to_lang = next(l for l in installed_languages if l.code == "es")

text = "Hello world"
translated_text = from_lang.get_translation(to_lang).translate(text)
print(translated_text)
