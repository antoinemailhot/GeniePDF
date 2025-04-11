# app/main_cli.py

import concurrent.futures

from data_structuring import pandas_processor
from data_structuring.aggregator import aggregate_results
from ocr import tesseract_engine
from pdf_tools import image_cleaner, pdf2image_wrapper
from repositories.pdf_repository import PdfRepository
from services.regex_parser import extract_data_with_regex
from utils.logger import init_logger
from utils.validator import validate_json

def main(config):
    """
    Fonction principale du mode CLI.
    Prend un objet `config` contenant tous les paramètres configurables.
    """
    logger = init_logger()

    # Création du repository
    pdf_repo = PdfRepository(config.pdf_input_directory)
    pdf_files = pdf_repo.get_all_pdfs()

    # Traitement parallèle (Future Pattern)
    with concurrent.futures.ThreadPoolExecutor(max_workers=config.max_workers) as executor:
        results = list(executor.map(process_pdf, pdf_files))

    # Agrégation
    final_data = aggregate_results(results)

    # Validation & export
    if validate_json(final_data):
        pdf_repo.save_extracted_data(final_data, config.json_output_path)
    else:
        logger.error("Validation JSON échouée")

def process_pdf(pdf_path):
    """
    Processus complet d’un PDF :
    1. Conversion PDF → image
    2. Nettoyage avec OpenCV
    3. OCR avec Tesseract
    4. Extraction avec regex
    5. Structuration avec pandas
    """
    images = pdf2image_wrapper.convert_pdf_to_images(pdf_path)
    processed_images = [image_cleaner.preprocess(img) for img in images]
    texts = [tesseract_engine.extract_text(img) for img in processed_images]
    extracted_data = [extract_data_with_regex(text) for text in texts]
    structured_data = pandas_processor.structurize(extracted_data)
    return structured_data
