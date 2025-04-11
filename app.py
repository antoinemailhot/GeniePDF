# app.py

import sys
import os

# Ajoute le dossier 'app/' au chemin d'importation
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))

import concurrent

from data_structuring import pandas_processor
from data_structuring.aggregator import aggregate_results
from ocr import tesseract_engine
from pdf_tools import image_cleaner, pdf2image_wrapper
from repositories.pdf_repository import PdfRepository
from services.regex_parser import extract_data_with_regex
from utils.config import config, load_config # Import de l'instance config.
from utils.logger import init_logger
from utils.validator import validate_json # Import de l'instance logger.


def main():
    # Chargement de la configuration
    config = load_config()  # via utils/config.py

    # Initialisation du logger pour le suivi des opérations
    logger = init_logger() # via utils/logger.py

     # Création du repository pour les PDF
    pdf_repo = PdfRepository(config.pdf_input_directory)

    # Récupérer la liste des fichiers PDF à traiter
    pdf_files = pdf_repo.get_all_pdfs()

    # Utilisation du Future Pattern pour lancer le traitement en parallèle
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(process_pdf, pdf_files))

    # Agrégation et export des résultats
    final_data = aggregate_results(results)

    if validate_json(final_data):  # Utilisation de JsonSchema
        pdf_repo.save_extracted_data(final_data, config.json_output_path)
    else:
        logger.error("Validation JSON échouée")

def process_pdf(pdf_path):
    """
    Processus complet d’un PDF :
    1. Extraction d’images via pdf2image
    2. Prétraitement des images (OpenCV)
    3. Application d’OCR (pytesseract)
    4. Extraction des informations via Regex
    5. Structuration des données (pandas et DTO)
    """
    # Conversion du PDF en images
    images = pdf2image_wrapper.convert_pdf_to_images(pdf_path)

    # Prétraitement des images
    processed_images = [image_cleaner.preprocess(img) for img in images]

    # Extraction du texte via OCR
    texts = [tesseract_engine.extract_text(img) for img in processed_images]

    # Extraction et nettoyage des données à l'aide de regex
    extracted_data = []
    for text in texts:
        data = extract_data_with_regex(text)
        extracted_data.append(data)

    # Structuration des données avec pandas
    structured_data = pandas_processor.structurize(extracted_data)

    # Retourner le DTO final pour ce PDF
    return structured_data

if __name__ == "__main__":
    main()
