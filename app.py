# app.py

import sys
import os
import argparse

# Ajoute le dossier 'app/' au chemin d'importation
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))

# Imports internes
from controllers.gui_controller import launch_gui
from utils.config import load_config
from main_cli import main as run_cli_main  # Importe le vrai traitement CLI

def create_parser():
    parser = argparse.ArgumentParser(description="Lance GeniePDF en mode CLI ou GUI.")
    parser.add_argument('--config', type=str, default='config.json', help="Fichier de configuration.")
    parser.add_argument('--input', type=str, help="Répertoire d'entrée des PDF.")
    parser.add_argument('--output', type=str, help="Fichier de sortie JSON.")
    parser.add_argument('--workers', type=int, default=5, help="Nombre de threads (par défaut: 5).")
    parser.add_argument('--verbose', action='store_true', help="Mode verbeux.")
    parser.add_argument('--gui', type=str, default="false", help="Lancer la GUI (true/false).")
    return parser

def dispatch():
    parser = create_parser()

    # Aucun argument → GUI par défaut
    if len(sys.argv) == 1:
        launch_gui()
        return

    # Arguments fournis
    args = parser.parse_args()
    use_gui = args.gui.lower() == "true"

    if use_gui:
        launch_gui(
            config_path=args.config,
            input_path=args.input,
            output_path=args.output,
            workers=args.workers
        )
    else:
        config = load_config(args.config)
        if args.input:
            config.pdf_input_directory = args.input
        if args.output:
            config.json_output_path = args.output
        config.max_workers = args.workers
        config.log_level = 'DEBUG' if args.verbose else 'INFO'

        run_cli_main(config)

if __name__ == "__main__":
    dispatch()
