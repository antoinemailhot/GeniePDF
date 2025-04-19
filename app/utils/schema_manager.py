import os
import importlib
from typing import Dict

SCHEMA_DIR = os.path.join(os.path.dirname(__file__), "schemas")
SCHEMA_MAP: Dict[str, dict] = {}

def load_schemas(schema_file: str = None) -> Dict[str, dict]:
    """
    Charge dynamiquement tous les schémas JSON du dossier 'schemas'.
    Si un fichier est spécifié, charge uniquement ce fichier.
    """
    global SCHEMA_MAP
    SCHEMA_MAP.clear()

    if schema_file:  # Si un fichier spécifique est donné
        module_name = schema_file[:-3]  # Suppression de l'extension .py
        import_path = f"utils.schemas.{module_name}"
        try:
            module = importlib.import_module(import_path)
            importlib.reload(module)
            if hasattr(module, "schema"):
                doc_type = module_name.replace("_schema", "").lower()
                SCHEMA_MAP[doc_type] = module.schema
        except Exception as e:
            print(f"❌ Erreur d'import {module_name} : {e}")
    else:
        # Charger tous les schémas dans le dossier 'schemas'
        for filename in os.listdir(SCHEMA_DIR):
            if filename.endswith(".py") and not filename.startswith("__"):
                module_name = filename[:-3]  # Suppression de l'extension .py
                import_path = f"utils.schemas.{module_name}"
                try:
                    module = importlib.import_module(import_path)
                    importlib.reload(module)
                    if hasattr(module, "schema"):
                        doc_type = module_name.replace("_schema", "").lower()
                        SCHEMA_MAP[doc_type] = module.schema
                except Exception as e:
                    print(f"❌ Erreur d'import {module_name} : {e}")

    if "default" not in SCHEMA_MAP:
        SCHEMA_MAP["default"] = {}

    return SCHEMA_MAP

def get_schema(doc_type: str) -> dict:
    """
    Récupère le schéma pour un type de document donné depuis SCHEMA_MAP.
    """
    return SCHEMA_MAP.get(doc_type, {})
