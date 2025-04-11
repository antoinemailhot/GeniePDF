# utils/config.py

import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env
load_dotenv()

class Config:
    """
    Classe de configuration pour GeniePDF avec des attributs d'instance.
    """

    def __init__(self):
        self.pdf_input_directory = os.getenv("PDF_INPUT_DIR", "data/input")
        self.json_output_path = os.getenv("JSON_OUTPUT_PATH", "data/output/results.json")
        self.tesseract_cmd = os.getenv("TESSERACT_CMD", "/usr/bin/tesseract")
        self.image_dpi = int(os.getenv("IMAGE_DPI", 300))
        self.max_workers = int(os.getenv("MAX_WORKERS", 5))
        self.log_level = os.getenv("LOG_LEVEL", "INFO")  # Optionnel

def load_config():
    return Config()

# Optionnel si tu veux accéder à config globalement
config = load_config()
