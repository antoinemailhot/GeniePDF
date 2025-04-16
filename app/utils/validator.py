import os
import jsonschema
from jsonschema import validate, ValidationError
from utils.schemas import base_schema, facture_schema, plan_schema, requisition_schema

SCHEMA_MAP = {
    "facture": facture_schema.schema,
    "plan": plan_schema.schema,
    "requisition": requisition_schema.schema,
    "default": base_schema.schema
}

def try_schema_validation(data, schema):
    try:
        validate(instance=data, schema=schema)
        return True
    except ValidationError:
        return False

def detect_document_type_by_schema(data):
    for doc_type, schema in SCHEMA_MAP.items():
        if doc_type == "default":
            continue
        if try_schema_validation(data, schema):
            return doc_type
    return "default"

def validate_json(data, file_path=None):
    """
    Valide les données JSON extraites selon un schéma détecté automatiquement.
    La détection repose d'abord sur la correspondance au schéma, et sinon, par le nom du fichier.
    """
    doc_type = detect_document_type(file_path) if file_path else "default"

    # Si la détection par nom échoue, on tente la détection par validation des schémas
    detected_by_structure = detect_document_type_by_schema(data)
    if detected_by_structure != "default":
        doc_type = detected_by_structure

    schema = SCHEMA_MAP.get(doc_type, base_schema.schema)

    try:
        validate(instance=data, schema=schema)
        return True
    except jsonschema.exceptions.ValidationError as e:
        print(f"❌ Erreur de validation JSON pour le fichier {file_path or 'inconnu'} (type: {doc_type}) : {e.message}")
        return False

def detect_document_type(file_path: str) -> str:
    """
    Détecte le type de document PDF selon le nom du fichier.

    :param file_path: Chemin du fichier PDF.
    :return: Type de document ('facture', 'plan', etc.)
    """
    filename = os.path.basename(file_path).lower()

    if "facture" in filename or "invoice" in filename:
        return "facture"
    elif "plan" in filename:
        return "plan"
    elif "order" in filename or "requisition" in filename:
        return "requisition"
    return "default"
