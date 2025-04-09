# tesseract_engine.py

import pytesseract
from PIL import Image

# Définir le chemin vers l'exécutable Tesseract si nécessaire
# Exemple pour un système Windows où Tesseract est installé à un emplacement spécifique :
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_text(image):
    """
    Extrait le texte d'une image en utilisant Tesseract OCR.

    :param image: Image PIL à partir de laquelle extraire le texte.
    :return: Le texte extrait de l'image.
    """
    # Conversion de l'image en texte avec pytesseract
    text = pytesseract.image_to_string(image)

    return text
