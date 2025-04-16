# GeniePDF
# Pour installer l'environnement suivre les étapes d'installation dans [requirements.txt](requirements.txt)

# Fonctionnement de l'application.
## Lancer en mode graphique (par défaut si aucun paramètre)
python app.py

## Lancer en CLI avec paramètres
python app.py --input data/ --output results.json --workers 3

## Lancer la GUI mais avec les paramètres appliqués
python app.py --gui true --input data/ --output results.json

# Pour se mettre dans son environnement : source .venv/bin/activate

# Installation 
# Comment installer les requirements :
# python -m venv .venv
# source .venv/bin/activate  OU .venv\Scripts\activate sur Windows
# pip install -r requirements.txt

# Ligne automatique : python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt

# Vous dever installer tesseract