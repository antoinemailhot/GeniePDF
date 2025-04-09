# main.py

import concurrent

from utils.config import config, load_config # Import de l'instance config.
from utils.logger import init_logger # Import de l'instance logger.


def main():
    # Chargement de la configuration
    config = load_config()  # via utils/config.py

    # Initialisation du logger pour le suivi des opérations
    logger = init_logger() # via utils/logger.py

    # Récupérer la liste des fichiers PDF à traiter
    pdf_files = get_pdf_files(config.pdf_input_directory)

    # Utilisation du Future Pattern pour lancer le traitement en parallèle
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(process_pdf, pdf_files))
    
    # Agrégation et export des résultats
    final_data = aggregate_results(results)
    if validate_json(final_data):  # Utilisation de JsonSchema
        export_to_json(final_data, config.json_output_path)
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
