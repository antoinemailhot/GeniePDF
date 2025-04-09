import os

class PdfRepository:
    def __init__(self, input_directory):
        """
        Repositoire pour accéder aux fichiers PDF dans le répertoire spécifié.

        :param input_directory: Répertoire où les fichiers PDF sont stockés.
        """
        self.input_directory = input_directory

    def get_all_pdfs(self):
        """
        Récupère tous les fichiers PDF dans le répertoire spécifié.

        :return: Liste des chemins de fichiers PDF.
        """
        pdf_files = [f for f in os.listdir(self.input_directory) if f.endswith('.pdf')]
        return pdf_files

    def save_extracted_data(self, extracted_data, output_path):
        """
        Sauvegarde les données extraites dans un fichier JSON ou autre format.

        :param extracted_data: Données extraites à sauvegarder.
        :param output_path: Chemin où le fichier sera sauvegardé.
        """
        # Implémentation pour sauvegarder les données, par exemple en JSON
        with open(output_path, 'w') as file:
            json.dump(extracted_data, file)
