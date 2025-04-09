# cli_controller.py

import argparse
import sys
from main import main
from utils.config import load_config  # Import de la fonction principale depuis main.py

def create_parser():
    """
    Crée et retourne un parser pour gérer les arguments CLI.
    """
    parser = argparse.ArgumentParser(description="Lance le traitement des fichiers PDF pour extraire des informations.")
    
    # Définition des arguments possibles
    parser.add_argument(
        '--config', 
        type=str, 
        default='config.json', 
        help="Le fichier de configuration à utiliser (par défaut: config.json)"
    )
    
    parser.add_argument(
        '--input', 
        type=str, 
        required=True, 
        help="Le répertoire contenant les fichiers PDF à traiter"
    )
    
    parser.add_argument(
        '--output', 
        type=str, 
        required=True, 
        help="Le répertoire où les résultats traités seront sauvegardés"
    )
    
    parser.add_argument(
        '--workers', 
        type=int, 
        default=5, 
        help="Le nombre de threads à utiliser pour le traitement parallèle (par défaut: 5)"
    )
    
    parser.add_argument(
        '--verbose', 
        action='store_true', 
        help="Activer le mode verbeux pour plus de logs"
    )
    
    return parser

def handle_args(args):
    """
    Gère les arguments CLI et lance l'application.
    """
    # Charger la configuration basée sur les arguments
    config = load_config(args.config)  # Vous pouvez adapter cela selon le format de votre config

    # Mettre à jour la configuration si des arguments spécifiques sont fournis
    config.pdf_input_directory = args.input
    config.json_output_path = args.output
    config.max_workers = args.workers

    # Initialiser le logger si mode verbeux est activé
    if args.verbose:
        config.log_level = 'DEBUG'
    else:
        config.log_level = 'INFO'

    # Appel de la fonction main avec la configuration modifiée
    main(config)

def main():
    """
    Fonction principale qui gère les arguments CLI et lance le traitement.
    """
    # Création du parser
    parser = create_parser()

    # Récupération des arguments
    args = parser.parse_args()

    # Traitement des arguments et lancement de l'application
    handle_args(args)

if __name__ == "__main__":
    main()
