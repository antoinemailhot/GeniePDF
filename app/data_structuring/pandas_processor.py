# pandas_processor.py

import pandas as pd

def structurize(extracted_data):
    """
    Structure les données extraites en un DataFrame pandas.

    :param extracted_data: Liste des données extraites de chaque PDF.
    :return: Un DataFrame pandas structuré avec les données extraites.
    """
    # Initialisation d'une liste pour stocker les lignes du DataFrame
    structured_data = []

    # Parcours des données extraites (chaque élément dans extracted_data correspond à un PDF)
    for data in extracted_data:
        # Chaque 'data' est un dictionnaire ou un format similaire qui peut être converti en ligne
        # Exemple de structure attendue pour chaque data : {'champ1': valeur1, 'champ2': valeur2, ...}
        structured_data.append(data)

    # Conversion des données structurées en DataFrame pandas
    df = pd.DataFrame(structured_data)

    

    return df
