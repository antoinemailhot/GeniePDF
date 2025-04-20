# tesseract_engine.py
import pytesseract
from PIL import Image

# Facultatif : définir explicitement le binaire
# pytesseract.pytesseract.tesseract_cmd = r"/usr/bin/tesseract"

DEFAULT_LANGS = "eng+fra"   # ← ajoute les langues ici

def extract_text(image, langs: str | None = None) -> str:
    """
    Extrait le texte d'une image en utilisant Tesseract OCR.
    :param image: Image PIL
    :param langs: ex. "eng" ou "fra" ou "eng+fra"; None → DEFAULT_LANGS
    """
    lang = langs or DEFAULT_LANGS
    # Possibilité d'ajouter des paramètres OEM/PSM si besoin
    custom_cfg = "--oem 3 --psm 6"
    return pytesseract.image_to_string(image, lang=lang, config=custom_cfg)
