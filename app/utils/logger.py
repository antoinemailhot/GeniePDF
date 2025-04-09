# utils/logger.py

import logging
import os
from datetime import datetime

def init_logger():
    """
    Initialise un logger avec un format clair et une sauvegarde dans un fichier.
    Retourne une instance de logger prête à l'emploi.
    """
    # Création du dossier de logs s'il n'existe pas
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)

    # Nom du fichier log avec timestamp
    log_filename = datetime.now().strftime("geniepdf_%Y-%m-%d_%H-%M-%S.log")
    log_path = os.path.join(log_dir, log_filename)

    # Configuration du logger
    logger = logging.getLogger("GeniePDFLogger")
    logger.setLevel(logging.DEBUG)

    # Éviter la duplication des handlers si le logger est déjà configuré
    if not logger.hasHandlers():
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # File handler
        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(logging.DEBUG)

        # Format commun
        formatter = logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)

        # Ajout des handlers au logger
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    return logger
