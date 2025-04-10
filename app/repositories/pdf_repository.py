import os
import json

class PdfRepository:
    def __init__(self, input_directory):
        """
        Répertoire pour accéder aux fichiers PDF dans le répertoire spécifié.

        :param input_directory: Répertoire où les fichiers PDF sont stockés.
        """
        if not os.path.isdir(input_directory):
            raise ValueError(f"Le répertoire spécifié n'existe pas : {input_directory}")
        self.input_directory = input_directory

    def get_all_pdfs(self, recursive=True):
        """
        Récupère tous les fichiers PDF dans le répertoire spécifié.

        :param recursive: Si True, parcourt récursivement les sous-dossiers.
        :return: Liste complète des chemins vers les fichiers PDF.
        """
        pdf_files = []
        if recursive:
            for root, _, files in os.walk(self.input_directory):
                for file in files:
                    if file.lower().endswith(".pdf"):
                        pdf_files.append(os.path.join(root, file))
        else:
            for file in os.listdir(self.input_directory):
                if file.lower().endswith(".pdf"):
                    pdf_files.append(os.path.join(self.input_directory, file))
        return pdf_files

    def save_extracted_data(self, extracted_data, output_path):
        """
        Sauvegarde les données extraites dans un fichier JSON.

        :param extracted_data: Données extraites à sauvegarder.
        :param output_path: Chemin de sortie du fichier.
        """
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as file:
            json.dump(extracted_data, file, ensure_ascii=False, indent=4)
