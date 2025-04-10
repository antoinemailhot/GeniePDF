# services/regex_parser.py

import re

def extract_data_with_regex(text):
    """
    Applique des regex pour extraire des données structurées du texte OCRisé.
    """
    data = {}

    # Extraction de numéro de dossier
    match_dossier = re.search(r"Dossier\s*:\s*(\w+)", text)
    if match_dossier:
        data["numero_dossier"] = match_dossier.group(1)

    # Extraction de date
    match_date = re.search(r"Date\s*:\s*(\d{2}/\d{2}/\d{4})", text)
    if match_date:
        data["date"] = match_date.group(1)

    return data
