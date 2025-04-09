# app/services/export_service.py

import json
import csv

class ExportService:
    def __init__(self):
        pass

    def export_to_json(self, data, output_path):
        """
        Exporte les données au format JSON.

        :param data: Données à exporter.
        :param output_path: Chemin du fichier de sortie.
        """
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=4)
    
    def export_to_csv(self, data, output_path):
        """
        Exporte les données au format CSV.

        :param data: Données à exporter.
        :param output_path: Chemin du fichier de sortie.
        """
        keys = data[0].keys()
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(data)
