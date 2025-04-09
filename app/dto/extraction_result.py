class ExtractionResult:
    def __init__(self, pdf_name, extracted_data):
        """
        Classe DTO pour stocker les résultats extraits d'un PDF.

        :param pdf_name: Nom du fichier PDF traité.
        :param extracted_data: Données extraites sous forme de liste de dictionnaires ou autres.
        """
        self.pdf_name = pdf_name
        self.extracted_data = extracted_data
    
    def to_dict(self):
        """
        Convertir l'objet en dictionnaire pour l'exportation JSON ou d'autres formats.

        :return: Un dictionnaire contenant le nom du PDF et les données extraites.
        """
        return {
            "pdf_name": self.pdf_name,
            "extracted_data": self.extracted_data
        }
