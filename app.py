# app.py

import sys
import os
import subprocess
import argparse

# Ajouter 'app/' au PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))

def ensure_env_and_restart_if_needed():
    """
    Vérifie si les dépendances critiques (ex: dotenv) sont manquantes.
    Si c’est le cas, crée un environnement virtuel `.venv`, installe les dépendances, puis relance le script.
    """
    try:
        from dotenv import load_dotenv  # test d'import
    except ModuleNotFoundError:
        print("❗ Dépendance manquante détectée : 'python-dotenv'")
        print("📦 Création de l’environnement virtuel et installation des dépendances...")

        venv_path = ".venv"

        # Crée le venv s'il n'existe pas
        if not os.path.isdir(venv_path):
            subprocess.check_call([sys.executable, "-m", "venv", venv_path])

        # Installer les paquets requis
        pip_exe = os.path.join(venv_path, "bin", "pip") if os.name != "nt" else os.path.join(venv_path, "Scripts", "pip.exe")
        subprocess.check_call([pip_exe, "install", "-r", "requirements.txt"])

        # Relance le script via l'interpréteur du venv
        python_exe = os.path.join(venv_path, "bin", "python") if os.name != "nt" else os.path.join(venv_path, "Scripts", "python.exe")
        print("🔁 Redémarrage automatique du script avec l’environnement virtuel...")
        os.execv(python_exe, [python_exe] + sys.argv)  # relance le script avec les mêmes arguments

# 🔁 On s'assure que l'environnement est prêt
ensure_env_and_restart_if_needed()

# À partir d'ici, les imports sont garantis
from controllers.gui_controller import launch_gui
from utils.config import load_config
from main_cli import main as run_cli_main

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
