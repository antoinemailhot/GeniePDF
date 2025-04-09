from app.services.classification_service import ClassificationService
from app.services.export_service import ExportService
from app.repositories.pdf_repository import PdfRepository
from app.dto.extraction_result import ExtractionResult

class ExtractionService:
    def __init__(self, config):
        self.pdf_repository = PdfRepository(config.pdf_input_directory)
        self.classification_service = ClassificationService()
        self.export_service = ExportService()
    
    def extract_and_classify(self):
        """
        Extraire les données des PDF, les classer, puis les exporter.
        """
        pdf_files = self.pdf_repository.get_all_pdfs()
        all_extracted_data = []

        for pdf_file in pdf_files:
            # Extraction des données du PDF
            extracted_data = self.extract_data_from_pdf(pdf_file)

            # Classification des données extraites
            classified_data = self.classification_service.classify_data(extracted_data)

            # Sauvegarde du résultat au format DTO
            extraction_result = ExtractionResult(pdf_file, classified_data)
            all_extracted_data.append(extraction_result.to_dict())

        # Exportation des résultats
        self.export_service.export_to_json(all_extracted_data, "output/extracted_data.json")

    def extract_data_from_pdf(self, pdf_file):
        """
        Extraire les données d'un fichier PDF.
        
        :param pdf_file: Nom du fichier PDF à traiter.
        :return: Données extraites sous forme de liste.
        """
        # Exemple d'appel à la fonction de traitement du PDF
        # C'est ici que le processus de OCR, nettoyage et extraction des données sera effectué
        # Cette méthode peut être liée à `process_pdf` dans main.py
        extracted_data = []  # Remplacer par la logique réelle
        return extracted_data
