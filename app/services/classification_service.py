class ClassificationService:
    def __init__(self):
        pass

    def classify_data(self, extracted_data):
        """
        Classifier les données extraites en catégories spécifiques.

        :param extracted_data: Données extraites à classifier.
        :return: Données classifiées.
        """
        # Implémentation de la logique de classification
        classified_data = {}
        for data in extracted_data:
            # Exemple de classification simple selon un critère
            category = self._classify_by_type(data)
            if category not in classified_data:
                classified_data[category] = []
            classified_data[category].append(data)
        
        return classified_data
    
    def _classify_by_type(self, data):
        """
        Déterminer la catégorie de la donnée.

        :param data: Donnée à classifier.
        :return: Catégorie de la donnée.
        """
        if "requisition" in data:
            return "requisition"
        else:
            return "miscellaneous"
