from pdf2image import convert_from_path
import os

def convert_pdf_to_images(pdf_path, dpi=300):
    """
    Convertit un fichier PDF en une liste d'images à partir des pages du PDF.

    :param pdf_path: Le chemin vers le fichier PDF à convertir.
    :param dpi: La résolution des images de sortie (par défaut 300 DPI).
    :return: Liste d'objets image PIL représentant les pages du PDF.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"Le fichier PDF à l'emplacement {pdf_path} n'existe pas.")

    try:
        # Utilisation de pdf2image pour convertir le PDF en images
        images = convert_from_path(pdf_path, dpi=dpi)
        return images
    except Exception as e:
        raise RuntimeError(f"Erreur lors de la conversion du PDF en images : {str(e)}")

