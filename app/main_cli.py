import concurrent.futures
import os
import pandas as pd
import json
from tqdm import tqdm
import importlib

from data_structuring import pandas_processor
from data_structuring.aggregator import aggregate_results
from ocr import tesseract_engine
from pdf_tools import image_cleaner, pdf2image_wrapper
from services.regex_parser import extract_data_with_regex
from utils.logger import init_logger
from utils.validator import validate_json
from utils.schema_manager import load_schemas


def main(config):
    """
    Fonction principale du mode CLI.
    Prend un objet `config` contenant tous les paramètres configurables.
    """
    logger = init_logger()
    pdf_input_directory = config.pdf_input_directory
    pdf_files = get_pdf_files(pdf_input_directory)

    if not pdf_files:
        logger.warning("Aucun fichier PDF trouvé dans le répertoire d'entrée.")
        return

    print(f"🔍 {len(pdf_files)} fichiers PDF trouvés. Lancement du traitement...")

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=config.max_workers) as executor:
        futures = {executor.submit(process_pdf, path): path for path in pdf_files}
        for future in tqdm(concurrent.futures.as_completed(futures), total=len(futures), desc="📄 Traitement"):
            try:
                results.append(future.result())
            except Exception as e:
                logger.error(f"Erreur lors du traitement de {futures[future]} : {e}")

    final_data = aggregate_results(results)

    json_ready_data = (
        final_data.to_dict(orient="records")
        if isinstance(final_data, pd.DataFrame) and not final_data.empty
        else []
    )

    # Charger le schéma dynamique pour validation
    schema = load_schemas(config.schema_file)  # Charge un seul schéma ou tous les schémas

    if validate_json(json_ready_data, schema):
        save_extracted_data(json_ready_data, config.json_output_path)
        print(f"✅ Données sauvegardées dans {config.json_output_path}")
    else:
        logger.error("❌ Validation JSON échouée")


def get_pdf_files(pdf_input_directory):
    """
    Récupère tous les fichiers PDF dans un répertoire donné.
    """
    pdf_files = []
    if os.path.isdir(pdf_input_directory):
        for root_dir, _, files in os.walk(pdf_input_directory):
            for f in files:
                if f.lower().endswith(".pdf"):
                    pdf_files.append(os.path.join(root_dir, f))
    elif os.path.isfile(pdf_input_directory) and pdf_input_directory.lower().endswith(".pdf"):
        pdf_files.append(pdf_input_directory)
    return pdf_files


def process_pdf(pdf_path):
    """
    Pipeline complet de traitement d’un fichier PDF :
    1. Conversion en images
    2. Nettoyage
    3. OCR
    4. Extraction via regex
    5. Structuration avec Pandas
    """
    images = pdf2image_wrapper.convert_pdf_to_images(pdf_path)
    processed_images = [image_cleaner.preprocess(img) for img in images]
    texts = [tesseract_engine.extract_text(img) for img in processed_images]
    extracted_data = [extract_data_with_regex(text) for text in texts]
    structured_data = pandas_processor.structurize(extracted_data, pdf_path)
    return structured_data


def save_extracted_data(data, output_path):
    """
    Sauvegarde les données extraites dans un fichier JSON.
    """
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
