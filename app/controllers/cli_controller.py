# cli_controller.py

import argparse
import sys
from app import main as run_cli_main  # main CLI
from utils.config import load_config

# Importe ta fonction GUI
from controllers.gui_controller import launch_gui  

def create_parser():
    """
    Crée et retourne un parser pour gérer les arguments CLI.
    """
    parser = argparse.ArgumentParser(description="Lance le traitement des fichiers PDF ou l'interface graphique.")
    
    parser.add_argument('--config', type=str, default='config.json', help="Fichier de configuration (par défaut: config.json)")
    parser.add_argument('--input', type=str, help="Répertoire d'entrée des PDF")
    parser.add_argument('--output', type=str, help="Fichier de sortie JSON")
    parser.add_argument('--workers', type=int, default=5, help="Nombre de threads (par défaut: 5)")
    parser.add_argument('--verbose', action='store_true', help="Mode verbeux")
    parser.add_argument('--gui', type=str, default="false", help="Lancer la GUI (true/false)")

    return parser

def handle_args(args):
    """
    Gère les arguments selon le mode (GUI ou CLI).
    """
    use_gui = args.gui.lower() == "true"

    if use_gui:
        # Lancement de l'interface graphique avec les paramètres CLI (facultatifs)
        launch_gui(config_path=args.config, input_path=args.input, output_path=args.output, workers=args.workers)
    else:
        # Chargement de la configuration
        config = load_config(args.config)

        # Mise à jour de la config avec les arguments CLI s'ils sont présents
        if args.input:
            config.pdf_input_directory = args.input
        if args.output:
            config.json_output_path = args.output
        config.max_workers = args.workers
        config.log_level = 'DEBUG' if args.verbose else 'INFO'

        # Lancement du traitement CLI
        run_cli_main(config)

def main():
    """
    Fonction principale qui détermine si on utilise le mode GUI ou CLI.
    """
    parser = create_parser()

    # Si aucun argument n'est passé, lancer la GUI
    if len(sys.argv) == 1:
        launch_gui()
    else:
        args = parser.parse_args()
        handle_args(args)

if __name__ == "__main__":
    main()
