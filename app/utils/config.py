# utils/config.py

import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

class Config:
    """
    Classe de configuration pour le projet GeniePDF.
    Permet de centraliser les paramètres tels que les chemins de fichiers et d'autres constantes.
    """
    # Chemins de répertoires et fichiers
    PDF_INPUT_DIR = os.getenv("PDF_INPUT_DIR", "data/input")  # Répertoire de lecture des fichiers PDF
    JSON_OUTPUT_PATH = os.getenv("JSON_OUTPUT_PATH", "data/output/results.json")  # Chemin du fichier JSON de sortie
    
    # Configuration pour Tesseract-OCR
    # Assurez-vous que le chemin vers l'exécutable tesseract est correct sur votre système
    TESSERACT_CMD = os.getenv("TESSERACT_CMD", "/usr/bin/tesseract")
    
    # Paramètres de conversion d'images
    IMAGE_DPI = int(os.getenv("IMAGE_DPI", 300))  # Résolution par défaut pour la conversion PDF en image
    
    # Paramètre pour le traitement parallèle (Future Pattern)
    MAX_WORKERS = int(os.getenv("MAX_WORKERS", 5))

# Instanciation de la configuration pour l'utilisation globale
config = Config()
